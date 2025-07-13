#!/usr/bin/env python3
"""
Simple test script to validate VPN Bot functionality
"""

import os
import sys
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    # Set minimal environment variables for testing
    os.environ['BOT_TOKEN'] = 'test_token_123456789'
    os.environ['ADMIN_IDS'] = '12345,67890'
    
    try:
        from bot.config.settings import Config, SUBSCRIPTION_PLANS
        
        # Test config validation
        assert Config.BOT_TOKEN == 'test_token_123456789'
        assert 12345 in Config.ADMIN_IDS
        assert 67890 in Config.ADMIN_IDS
        
        # Test subscription plans
        assert '1_month' in SUBSCRIPTION_PLANS
        assert SUBSCRIPTION_PLANS['1_month']['price'] == 299
        
        print("✅ Configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_database():
    """Test database models"""
    print("🗄️ Testing database models...")
    
    try:
        from bot.models.database import DatabaseManager, User, Subscription, Payment
        
        # Use temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_url = f"sqlite:///{tmp.name}"
        
        # Initialize database
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # Test creating a user
        session = db_manager.get_session()
        user = User(
            telegram_id=123456789,
            username='test_user',
            first_name='Test',
            last_name='User',
            referral_code='TEST123'
        )
        session.add(user)
        session.commit()
        
        # Test querying user
        found_user = session.query(User).filter_by(telegram_id=123456789).first()
        assert found_user is not None
        assert found_user.username == 'test_user'
        assert found_user.full_name == 'Test User'
        
        session.close()
        db_manager.close()
        
        # Clean up
        os.unlink(tmp.name)
        
        print("✅ Database test passed")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_localization():
    """Test localization"""
    print("🌐 Testing localization...")
    
    try:
        from locales.ru import get_message, MESSAGES
        
        # Test message retrieval
        welcome_msg = get_message('welcome')
        assert 'Добро пожаловать' in welcome_msg
        
        # Test message formatting
        plan_msg = get_message('plan_template', 
                              name='Тест план', 
                              price=299, 
                              duration=30,
                              description='Тестовое описание')
        assert 'Тест план' in plan_msg
        assert '299' in plan_msg
        
        print("✅ Localization test passed")
        return True
    except Exception as e:
        print(f"❌ Localization test failed: {e}")
        return False


def test_utilities():
    """Test utility functions"""
    print("🛠️ Testing utilities...")
    
    try:
        from bot.utils.helpers import (
            generate_referral_code, 
            calculate_end_date,
            format_currency,
            generate_payment_id
        )
        
        # Test referral code generation
        ref_code = generate_referral_code()
        assert len(ref_code) == 8
        assert ref_code.isalnum()
        
        # Test currency formatting
        formatted = format_currency(29900)  # 299 rubles in kopecks
        assert '299' in formatted
        assert '₽' in formatted
        
        # Test payment ID generation
        payment_id = generate_payment_id()
        assert 'VPN_' in payment_id
        
        # Test end date calculation
        end_date = calculate_end_date('1_month')
        assert end_date > datetime.utcnow()
        
        print("✅ Utilities test passed")
        return True
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting VPN Bot functionality tests...\n")
    
    tests = [
        test_config,
        test_database,
        test_localization,
        test_utilities
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)