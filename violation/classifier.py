# Violation types with severity scores
VIOLATIONS = {
    'no_helmet': {
        'name': 'No Helmet',
        'severity': 7.2,
        'risk': 'HIGH',
        'color': (0, 165, 255)  # Orange
    },
    'triple_riding': {
        'name': 'Triple Riding',
        'severity': 6.5,
        'risk': 'HIGH',
        'color': (0, 165, 255)
    },
    'wrong_side': {
        'name': 'Wrong Side Driving',
        'severity': 9.4,
        'risk': 'CRITICAL',
        'color': (0, 0, 255)  # Red
    },
    'stop_line': {
        'name': 'Stop Line Violation',
        'severity': 6.0,
        'risk': 'MEDIUM',
        'color': (0, 255, 255)  # Yellow
    },
    'red_light': {
        'name': 'Red Light Jump',
        'severity': 8.5,
        'risk': 'CRITICAL',
        'color': (0, 0, 255)
    },
    'illegal_parking': {
        'name': 'Illegal Parking',
        'severity': 4.1,
        'risk': 'MEDIUM',
        'color': (255, 255, 0)
    },
    'no_seatbelt': {
        'name': 'No Seatbelt',
        'severity': 6.8,
        'risk': 'HIGH',
        'color': (0, 165, 255)
    }
}

def get_severity(violation_type):
    """Get severity score for a violation"""
    v = VIOLATIONS.get(violation_type, {})
    return {
        'severity': v.get('severity', 5.0),
        'risk': v.get('risk', 'MEDIUM'),
        'color': v.get('color', (255, 255, 0))
    }

def get_risk_emoji(risk):
    """Get emoji for risk level"""
    return {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }.get(risk, '🟡')

if __name__ == "__main__":
    print("✅ Violation classifier ready!")
    for k, v in VIOLATIONS.items():
        emoji = get_risk_emoji(v['risk'])
        print(f"{emoji} {v['name']} | Severity: {v['severity']}/10")