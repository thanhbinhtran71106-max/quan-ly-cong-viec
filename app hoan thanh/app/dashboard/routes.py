from flask import render_template
from app.dashboard import dashboard_bp
from app.auth.decorators import token_required

@dashboard_bp.route('/dashboard')
@token_required
def index(current_user):
    stats = {
        'total_devices': 124,
        'active_devices': 118,
        'offline_devices': 6,
        'alerts': 2
    }
    return render_template('dashboard.html', stats=stats, current_user=current_user)
