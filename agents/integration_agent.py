"""
Integration Agent - Generates code for third-party integrations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from planner import FileSpec


@dataclass
class IntegrationSpec:
    """Specification for a third-party integration."""
    name: str
    type: str
    config: Dict
    endpoints: List[str]
    dependencies: List[str]


class IntegrationAgent:
    """Agent responsible for generating integration code."""
    
    def __init__(self):
        self.supported_integrations = {
            'payment': self._generate_payment_integration,
            'authentication': self._generate_auth_integration,
            'email': self._generate_email_integration,
            'sms': self._generate_sms_integration,
            'cloud': self._generate_cloud_integration,
            'analytics': self._generate_analytics_integration,
        }
    
    def generate_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate integration code for a specific file."""
        integration_type = self._determine_integration_type(file_spec)
        
        if integration_type not in self.supported_integrations:
            return self._generate_generic_integration(file_spec, project_context)
        
        generator = self.supported_integrations[integration_type]
        return generator(file_spec, project_context)
    
    def _determine_integration_type(self, file_spec: FileSpec) -> str:
        """Determine the type of integration based on file spec."""
        file_name = file_spec.path.split('/')[-1].lower()
        
        if 'payment' in file_name or 'stripe' in file_name:
            return 'payment'
        elif 'auth' in file_name or 'oauth' in file_name:
            return 'authentication'
        elif 'email' in file_name or 'mail' in file_name:
            return 'email'
        elif 'sms' in file_name or 'twilio' in file_name:
            return 'sms'
        elif 'cloud' in file_name or 'aws' in file_name or 'azure' in file_name:
            return 'cloud'
        elif 'analytics' in file_name or 'tracking' in file_name:
            return 'analytics'
        else:
            return 'generic'
    
    def _generate_payment_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate payment integration code (Stripe)."""
        return """
import stripe
import os
from fastapi import HTTPException
from typing import Dict, Any
from decimal import Decimal

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class PaymentService:
    \"\"\"Service for handling payment operations with Stripe.\"\"\"
    
    def __init__(self):
        self.stripe = stripe
    
    async def create_payment_intent(self, amount: int, currency: str = "usd", metadata: Dict = None) -> Dict[str, Any]:
        \"\"\"Create a payment intent for a given amount.\"\"\"
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency,
                'status': intent.status
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        \"\"\"Confirm a payment intent.\"\"\"
        try:
            intent = self.stripe.PaymentIntent.confirm(payment_intent_id)
            return {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount': intent.amount,
                'currency': intent.currency
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        \"\"\"Get a payment intent by ID.\"\"\"
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount': intent.amount,
                'currency': intent.currency,
                'created': intent.created
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    async def create_customer(self, email: str, name: str = None) -> Dict[str, Any]:
        \"\"\"Create a new customer.\"\"\"
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name
            )
            return {
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name,
                'created': customer.created
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        \"\"\"Create a subscription for a customer.\"\"\"
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            return {
                'subscription_id': subscription.id,
                'status': subscription.status,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'current_period_end': subscription.current_period_end
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        \"\"\"Handle Stripe webhook events.\"\"\"
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Handle successful payment
            return {'status': 'success', 'payment_intent_id': payment_intent['id']}
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Handle failed payment
            return {'status': 'failed', 'payment_intent_id': payment_intent['id']}
        else:
            return {'status': 'unhandled', 'event_type': event['type']}

# Global payment service instance
payment_service = PaymentService()
""".strip()
    
    def _generate_auth_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate OAuth integration code."""
        return """
import os
import httpx
from fastapi import HTTPException
from typing import Dict, Any, Optional
from urllib.parse import urlencode

class OAuthService:
    \"\"\"Service for handling OAuth integrations.\"\"\"
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    def get_google_auth_url(self, state: str = None) -> str:
        \"\"\"Generate Google OAuth authorization URL.\"\"\"
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    def get_github_auth_url(self, state: str = None) -> str:
        \"\"\"Generate GitHub OAuth authorization URL.\"\"\"
        params = {
            'client_id': self.github_client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user:email',
            'response_type': 'code'
        }
        
        if state:
            params['state'] = state
        
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    async def exchange_google_code(self, code: str) -> Dict[str, Any]:
        \"\"\"Exchange Google authorization code for access token.\"\"\"
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            return response.json()
    
    async def exchange_github_code(self, code: str) -> Dict[str, Any]:
        \"\"\"Exchange GitHub authorization code for access token.\"\"\"
        token_url = "https://github.com/login/oauth/access_token"
        
        data = {
            'client_id': self.github_client_id,
            'client_secret': self.github_client_secret,
            'code': code
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        \"\"\"Get Google user information using access token.\"\"\"
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            return response.json()
    
    async def get_github_user_info(self, access_token: str) -> Dict[str, Any]:
        \"\"\"Get GitHub user information using access token.\"\"\"
        user_info_url = "https://api.github.com/user"
        
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            return response.json()

# Global OAuth service instance
oauth_service = OAuthService()
""".strip()
    
    def _generate_email_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate email integration code."""
        return """
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from fastapi import HTTPException
import httpx

class EmailService:
    \"\"\"Service for handling email operations.\"\"\"
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    
    async def send_email_smtp(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        from_email: str = None,
        is_html: bool = False
    ) -> bool:
        \"\"\"Send email using SMTP.\"\"\"
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email or self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(from_email or self.smtp_username, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    async def send_email_sendgrid(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        from_email: str = None,
        is_html: bool = False
    ) -> bool:
        \"\"\"Send email using SendGrid API.\"\"\"
        if not self.sendgrid_api_key:
            raise HTTPException(status_code=500, detail="SendGrid API key not configured")
        
        url = "https://api.sendgrid.com/v3/mail/send"
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {"email": from_email or "noreply@example.com"},
            "content": [
                {
                    "type": "text/html" if is_html else "text/plain",
                    "value": body
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            
            if response.status_code not in [200, 202]:
                raise HTTPException(status_code=500, detail="Failed to send email via SendGrid")
            
            return True
    
    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        \"\"\"Send welcome email to new user.\"\"\"
        subject = "Welcome to Our Platform!"
        body = f\"\"\"
        <html>
        <body>
            <h2>Welcome, {name}!</h2>
            <p>Thank you for joining our platform. We're excited to have you on board.</p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Best regards,<br>The Team</p>
        </body>
        </html>
        \"\"\"
        
        return await self.send_email_sendgrid(to_email, subject, body, is_html=True)
    
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        \"\"\"Send password reset email.\"\"\"
        subject = "Password Reset Request"
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        body = f\"\"\"
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
        </body>
        </html>
        \"\"\"
        
        return await self.send_email_sendgrid(to_email, subject, body, is_html=True)

# Global email service instance
email_service = EmailService()
""".strip()
    
    def _generate_sms_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate SMS integration code (Twilio)."""
        return """
import os
from twilio.rest import Client
from typing import Dict, Any
from fastapi import HTTPException

class SMSService:
    \"\"\"Service for handling SMS operations with Twilio.\"\"\"
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    async def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        \"\"\"Send SMS message.\"\"\"
        if not self.client:
            raise HTTPException(status_code=500, detail="Twilio not configured")
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )
            
            return {
                'sid': message_obj.sid,
                'status': message_obj.status,
                'to': message_obj.to,
                'from': message_obj.from_,
                'date_sent': message_obj.date_sent
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")
    
    async def send_verification_code(self, to_phone: str, code: str) -> Dict[str, Any]:
        \"\"\"Send verification code via SMS.\"\"\"
        message = f"Your verification code is: {code}. This code will expire in 10 minutes."
        return await self.send_sms(to_phone, message)
    
    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        \"\"\"Get status of a sent message.\"\"\"
        if not self.client:
            raise HTTPException(status_code=500, detail="Twilio not configured")
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Message not found: {str(e)}")

# Global SMS service instance
sms_service = SMSService()
""".strip()
    
    def _generate_cloud_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate cloud integration code (AWS S3)."""
        return """
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from fastapi import HTTPException, UploadFile
import uuid

class CloudStorageService:
    \"\"\"Service for handling cloud storage operations with AWS S3.\"\"\"
    
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        
        if self.aws_access_key_id and self.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
        else:
            self.s3_client = None
    
    async def upload_file(self, file: UploadFile, folder: str = "") -> Dict[str, Any]:
        \"\"\"Upload file to S3.\"\"\"
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="AWS S3 not configured")
        
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Add folder prefix if specified
            s3_key = f"{folder}/{unique_filename}" if folder else unique_filename
            
            # Upload file
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type
            )
            
            # Generate file URL
            file_url = f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            return {
                'file_url': file_url,
                's3_key': s3_key,
                'original_filename': file.filename,
                'file_size': len(file_content),
                'content_type': file.content_type
            }
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    async def delete_file(self, s3_key: str) -> bool:
        \"\"\"Delete file from S3.\"\"\"
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="AWS S3 not configured")
        
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    async def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        \"\"\"Generate presigned URL for file access.\"\"\"
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="AWS S3 not configured")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate URL: {str(e)}")
    
    async def list_files(self, folder: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        \"\"\"List files in S3 bucket.\"\"\"
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="AWS S3 not configured")
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=folder,
                MaxKeys=limit
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{obj['Key']}"
                })
            
            return files
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

# Global cloud storage service instance
cloud_storage_service = CloudStorageService()
""".strip()
    
    def _generate_analytics_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate analytics integration code."""
        return """
import os
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
from datetime import datetime

class AnalyticsService:
    \"\"\"Service for handling analytics and tracking.\"\"\"
    
    def __init__(self):
        self.google_analytics_id = os.getenv("GOOGLE_ANALYTICS_ID")
        self.mixpanel_token = os.getenv("MIXPANEL_TOKEN")
    
    async def track_event(self, event_name: str, properties: Dict[str, Any], user_id: str = None) -> bool:
        \"\"\"Track an event with analytics service.\"\"\"
        if self.mixpanel_token:
            return await self._track_mixpanel_event(event_name, properties, user_id)
        else:
            # Fallback to custom analytics
            return await self._track_custom_event(event_name, properties, user_id)
    
    async def _track_mixpanel_event(self, event_name: str, properties: Dict[str, Any], user_id: str = None) -> bool:
        \"\"\"Track event using Mixpanel.\"\"\"
        url = "https://api.mixpanel.com/track"
        
        data = {
            "event": event_name,
            "properties": {
                "token": self.mixpanel_token,
                "time": int(datetime.now().timestamp()),
                **properties
            }
        }
        
        if user_id:
            data["properties"]["distinct_id"] = user_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                return response.status_code == 200
        except Exception:
            return False
    
    async def _track_custom_event(self, event_name: str, properties: Dict[str, Any], user_id: str = None) -> bool:
        \"\"\"Track event using custom analytics (placeholder).\"\"\"
        # TODO: Implement custom analytics tracking
        print(f"Event: {event_name}, Properties: {properties}, User: {user_id}")
        return True
    
    async def track_page_view(self, page_path: str, user_id: str = None, additional_properties: Dict[str, Any] = None) -> bool:
        \"\"\"Track page view.\"\"\"
        properties = {
            "page_path": page_path,
            "timestamp": datetime.now().isoformat(),
            **(additional_properties or {})
        }
        
        return await self.track_event("page_view", properties, user_id)
    
    async def track_user_action(self, action: str, user_id: str, properties: Dict[str, Any] = None) -> bool:
        \"\"\"Track user action.\"\"\"
        event_properties = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            **(properties or {})
        }
        
        return await self.track_event("user_action", event_properties, user_id)
    
    async def track_conversion(self, conversion_type: str, value: float = None, user_id: str = None) -> bool:
        \"\"\"Track conversion event.\"\"\"
        properties = {
            "conversion_type": conversion_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if value is not None:
            properties["value"] = value
        
        return await self.track_event("conversion", properties, user_id)
    
    async def get_analytics_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        \"\"\"Get analytics data for date range.\"\"\"
        # TODO: Implement analytics data retrieval
        return {
            "start_date": start_date,
            "end_date": end_date,
            "page_views": 0,
            "unique_visitors": 0,
            "conversions": 0
        }

# Global analytics service instance
analytics_service = AnalyticsService()
""".strip()
    
    def _generate_generic_integration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate generic integration code."""
        return f"""
# {file_spec.description}
# Generated integration file: {file_spec.path}

import os
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException

class GenericIntegrationService:
    \"\"\"Generic integration service.\"\"\"
    
    def __init__(self):
        self.api_key = os.getenv("INTEGRATION_API_KEY")
        self.base_url = os.getenv("INTEGRATION_BASE_URL", "https://api.example.com")
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        \"\"\"Make HTTP request to integration API.\"\"\"
        url = f"{{self.base_url}}/{{endpoint}}"
        
        headers = {{
            "Authorization": f"Bearer {{self.api_key}}",
            "Content-Type": "application/json"
        }}
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=400, detail="Unsupported HTTP method")
            
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        \"\"\"Check integration service health.\"\"\"
        try:
            result = await self.make_request("GET", "health")
            return {{"status": "healthy", "integration": "available"}}
        except Exception as e:
            return {{"status": "unhealthy", "error": str(e)}}

# Global integration service instance
integration_service = GenericIntegrationService()
""".strip()