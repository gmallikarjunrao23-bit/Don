"""
OSINT 100X ULTIMATE — Payment Service
"""

from datetime import datetime, timedelta
from flask import current_app, request
from app import db
from app.models.payment import Payment
from app.models.user import User
from app.models.audit import AuditLog
from app.exceptions import PaymentError

class PaymentService:
    """Service for payment operations"""
    
    @staticmethod
    def create_payment(user, tier, transaction_id, screenshot_url=None):
        """Create a new payment record"""
        
        if tier not in current_app.config['TIERS']:
            raise PaymentError('Invalid tier selected')
        
        tier_info = current_app.config['TIERS'][tier]
        
        # Check if transaction ID already exists
        existing = Payment.query.filter_by(transaction_id=transaction_id).first()
        if existing:
            raise PaymentError('Transaction ID already submitted')
        
        payment = Payment(
            user_id=user.id,
            amount=tier_info['price'],
            tier=tier,
            transaction_id=transaction_id,
            screenshot_url=screenshot_url or '/static/uploads/pending.png',
            upi_id=current_app.config['UPI_ID'],
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action='payment_submit',
            resource='payment',
            resource_id=transaction_id,
            details=f"Payment submitted for {tier} plan (₹{tier_info['price']})",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        return payment
    
    @staticmethod
    def approve_payment(payment_id, admin_id):
        """Approve a payment and upgrade user"""
        
        payment = Payment.query.get(payment_id)
        if not payment:
            raise PaymentError('Payment not found')
        
        if payment.status != 'pending':
            raise PaymentError(f'Payment already {payment.status}')
        
        payment.status = 'approved'
        payment.approved_at = datetime.utcnow()
        payment.admin_id = admin_id
        
        # Upgrade user
        user = User.query.get(payment.user_id)
        if user:
            user.tier = payment.tier
            user.premium_expiry = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            user_id=admin_id,
            action='payment_approve',
            resource='payment',
            resource_id=payment.transaction_id,
            details=f"Payment approved for user {user.user_id} ({payment.tier})",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        return payment
    
    @staticmethod
    def reject_payment(payment_id, admin_id, reason):
        """Reject a payment"""
        
        payment = Payment.query.get(payment_id)
        if not payment:
            raise PaymentError('Payment not found')
        
        if payment.status != 'pending':
            raise PaymentError(f'Payment already {payment.status}')
        
        payment.status = 'rejected'
        payment.admin_notes = reason
        payment.admin_id = admin_id
        
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            user_id=admin_id,
            action='payment_reject',
            resource='payment',
            resource_id=payment.transaction_id,
            details=f"Payment rejected: {reason}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit)
        db.session.commit()
        
        return payment
    
    @staticmethod
    def get_user_payments(user):
        return Payment.query.filter_by(user_id=user.id)\
            .order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_pending_payments():
        return Payment.query.filter_by(status='pending')\
            .order_by(Payment.created_at.asc()).all()
