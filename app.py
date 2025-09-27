from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import json
import os
import hashlib

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_NAME = 'healthshield.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Users table with password field
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            village TEXT NOT NULL,
            mobile TEXT,
            email TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analysis history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symptoms TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            matching_diseases TEXT,
            analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Disease symptoms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            symptoms TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            precautions TEXT,
            icon TEXT
        )
    ''')
    
    # Exercise recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_level TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            frequency TEXT,
            icon TEXT,
            benefits TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Insert default data
    insert_default_diseases()
    insert_default_exercises()

def insert_default_diseases():
    """Insert default disease data into the database without duplicates"""
    default_diseases = [
        {
            "name": "Typhoid Fever",
            "symptoms": json.dumps(["Fever", "Headache", "Stomach Ache", "Diarrhea", "Weakness"]),
            "description": "A bacterial infection caused by Salmonella typhi, often spread through contaminated water or food.",
            "severity": "High",
            "precautions": json.dumps(["Drink boiled or purified water", "Maintain proper hygiene", "Seek medical attention immediately"]),
            "icon": "fas fa-bacteria"
        },
        {
            "name": "Cholera", 
            "symptoms": json.dumps(["Diarrhea", "Vomiting", "Dehydration", "Stomach Ache"]),
            "description": "An acute diarrheal illness caused by infection of the intestine with Vibrio cholerae bacteria.",
            "severity": "High",
            "precautions": json.dumps(["Rehydrate frequently", "Use oral rehydration solutions", "Seek emergency care if severe"]),
            "icon": "fas fa-tint-slash"
        },
        {
            "name": "Hepatitis A",
            "symptoms": json.dumps(["Jaundice", "Fever", "Vomiting", "Stomach Ache", "Weakness"]),
            "description": "A highly contagious liver infection caused by the hepatitis A virus, often spread through contaminated water.",
            "severity": "Medium",
            "precautions": json.dumps(["Get vaccinated", "Practice good hygiene", "Avoid raw or undercooked shellfish"]),
            "icon": "fas fa-liver"
        },
        {
            "name": "Dysentery",
            "symptoms": json.dumps(["Blood in Stool", "Diarrhea", "Fever", "Stomach Ache", "Dehydration"]),
            "description": "An intestinal inflammation, especially in the colon, that can lead to severe diarrhea with blood or mucus.",
            "severity": "Medium",
            "precautions": json.dumps(["Drink plenty of fluids", "Maintain sanitation", "Cook food thoroughly"]),
            "icon": "fas fa-procedures"
        },
        {
            "name": "Giardiasis",
            "symptoms": json.dumps(["Diarrhea", "Stomach Ache", "Vomiting", "Dehydration", "Weakness"]),
            "description": "An intestinal infection caused by the giardia parasite, spread through contaminated water sources.",
            "severity": "Medium",
            "precautions": json.dumps(["Use water filters", "Avoid swallowing pool water", "Practice good hand hygiene"]),
            "icon": "fas fa-parasite"
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for disease in default_diseases:
        cursor.execute('''
            INSERT OR IGNORE INTO diseases (name, symptoms, description, severity, precautions, icon)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (disease['name'], disease['symptoms'], disease['description'], 
              disease['severity'], disease['precautions'], disease['icon']))
    
    conn.commit()
    conn.close()

def insert_default_exercises():
    """Insert default exercise recommendations"""
    default_exercises = [
        # High risk exercises
        {
            "risk_level": "high",
            "name": "Gentle Walking",
            "description": "Start with 5-10 minutes of slow walking daily. Focus on maintaining hydration.",
            "duration": "5-10 minutes",
            "frequency": "Daily",
            "icon": "fas fa-walking",
            "benefits": "Improves circulation without overexertion"
        },
        {
            "risk_level": "high",
            "name": "Breathing Exercises",
            "description": "Practice deep breathing to reduce stress and improve oxygen flow.",
            "duration": "5 minutes",
            "frequency": "2-3 times daily",
            "icon": "fas fa-wind",
            "benefits": "Reduces stress, improves lung capacity"
        },
        # Medium risk exercises
        {
            "risk_level": "medium",
            "name": "Brisk Walking",
            "description": "Increase to 15-20 minutes of brisk walking to improve circulation.",
            "duration": "15-20 minutes",
            "frequency": "Daily",
            "icon": "fas fa-walking",
            "benefits": "Improves cardiovascular health"
        },
        {
            "risk_level": "medium",
            "name": "Yoga",
            "description": "Gentle yoga poses to improve flexibility and reduce stress.",
            "duration": "10-15 minutes",
            "frequency": "3-4 times weekly",
            "icon": "fas fa-spa",
            "benefits": "Improves flexibility and mental wellbeing"
        },
        # Low risk exercises
        {
            "risk_level": "low",
            "name": "Cardiovascular Exercise",
            "description": "30 minutes of moderate-intensity exercise like jogging or cycling.",
            "duration": "30 minutes",
            "frequency": "3-5 times weekly",
            "icon": "fas fa-heartbeat",
            "benefits": "Improves heart health and endurance"
        },
        {
            "risk_level": "low",
            "name": "Strength Training",
            "description": "Full-body strength workout with weights or resistance bands.",
            "duration": "20-30 minutes",
            "frequency": "2-3 times weekly",
            "icon": "fas fa-dumbbell",
            "benefits": "Builds muscle mass and strength"
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for exercise in default_exercises:
        cursor.execute('''
            INSERT OR IGNORE INTO exercises (risk_level, name, description, duration, frequency, icon, benefits)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (exercise['risk_level'], exercise['name'], exercise['description'],
              exercise['duration'], exercise['frequency'], exercise['icon'], exercise['benefits']))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def generate_password(name, age):
    """Generate password from name and age"""
    # Remove spaces from name and combine with age
    clean_name = name.replace(' ', '').lower()
    password_string = f"{clean_name}{age}"
    return hashlib.md5(password_string.encode()).hexdigest()

def verify_password(password, name, age):
    """Verify if the provided password matches the generated password"""
    expected_password = generate_password(name, age)
    return password == expected_password

# Symptom mapping
SYMPTOM_MAPPING = {
    1: {"name": "Fever", "icon": "fas fa-thermometer-half", "severity": "Medium"},
    2: {"name": "Stomach Ache", "icon": "fas fa-stomach", "severity": "Low"},
    3: {"name": "Vomiting", "icon": "fas fa-procedures", "severity": "Medium"},
    4: {"name": "Headache", "icon": "fas fa-head-side-virus", "severity": "Low"},
    5: {"name": "Dehydration", "icon": "fas fa-tint-slash", "severity": "High"},
    6: {"name": "Jaundice", "icon": "fas fa-sun", "severity": "High"},
    7: {"name": "Rash", "icon": "fas fa-allergies", "severity": "Low"},
    8: {"name": "Weakness", "icon": "fas fa-tired", "severity": "Low"},
    9: {"name": "Diarrhea", "icon": "fas fa-toilet", "severity": "Medium"},
    10: {"name": "Muscle Aches", "icon": "fas fa-dumbbell", "severity": "Low"},
    11: {"name": "Blood in Stool", "icon": "fas fa-tint", "severity": "High"},
    12: {"name": "Cough", "icon": "fas fa-lungs-virus", "severity": "Low"}
}

class UserManager:
    """Manage user data and analysis history"""
    
    def create_user(self, user_data):
        """Create a new user with generated password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            print(f"Creating user: {user_data['name']}, {user_data['age']}, {user_data['village']}")
            
            # Generate password from name and age
            password = generate_password(user_data['name'], user_data['age'])
            
            # Check if user already exists
            cursor.execute('''
                SELECT id FROM users 
                WHERE name = ? AND age = ? AND village = ? AND gender = ?
            ''', (user_data['name'], user_data['age'], user_data['village'], user_data['gender']))
            
            existing_user = cursor.fetchone()
            
            if existing_user:
                user_id = existing_user['id']
                print(f"User already exists with ID: {user_id}")
                return user_id
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (name, age, gender, village, mobile, email, password)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['name'], 
                    user_data['age'], 
                    user_data['gender'],
                    user_data['village'], 
                    user_data.get('mobile'), 
                    user_data.get('email'), 
                    password
                ))
                
                user_id = cursor.lastrowid
                conn.commit()
                print(f"Created new user with ID: {user_id}")
                return user_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error in create_user: {str(e)}")
            raise e
        finally:
            conn.close()
    
    def authenticate_user(self, user_id, password):
        """Authenticate user with ID and password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user:
                # Verify password
                if verify_password(password, user['name'], user['age']):
                    return dict(user)
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Error in authenticate_user: {str(e)}")
            return None
        finally:
            conn.close()
    
    def save_analysis(self, user_id, symptoms, risk_level, risk_score, matching_diseases):
        """Save analysis results to history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO analysis_history (user_id, symptoms, risk_level, risk_score, matching_diseases)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, json.dumps(symptoms), risk_level, risk_score, 
                  json.dumps(matching_diseases) if matching_diseases else None))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving analysis: {str(e)}")
            raise e
        finally:
            conn.close()
    
    def get_user_history(self, user_id):
        """Get analysis history for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_history 
            WHERE user_id = ? 
            ORDER BY analysis_timestamp DESC
            LIMIT 10
        ''', (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in history]
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_analyses,
                AVG(risk_score) as avg_risk_score,
                MAX(analysis_timestamp) as last_analysis
            FROM analysis_history 
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return {
                'total_analyses': stats['total_analyses'] or 0,
                'avg_risk_score': float(stats['avg_risk_score'] or 0),
                'last_analysis': stats['last_analysis']
            }
        return None

    def get_all_users(self):
        """Get all users from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, age, gender, village, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        return [dict(user) for user in users]

class SymptomAnalyzer:
    """Enhanced symptom analysis with database integration"""
    
    def get_diseases_from_db(self):
        """Retrieve diseases from database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM diseases ORDER BY id')
        diseases = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in diseases]
    
    def get_exercises_by_risk_level(self, risk_level):
        """Get exercise recommendations for a specific risk level"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM exercises WHERE risk_level = ? ORDER BY id', (risk_level,))
        exercises = cursor.fetchall()
        conn.close()
        
        return [dict(exercise) for exercise in exercises]
    
    def analyze_symptoms(self, selected_symptom_ids):
        """Analyze symptoms using diseases from database"""
        diseases_data = self.get_diseases_from_db()
        
        # Convert database diseases to analysis format
        processed_diseases = []
        for disease in diseases_data:
            processed_diseases.append({
                "id": disease['id'],
                "name": disease['name'],
                "symptoms": json.loads(disease['symptoms']),
                "description": disease['description'],
                "severity": disease['severity'],
                "precautions": json.loads(disease['precautions']),
                "icon": disease['icon']
            })
        
        # Rest of analysis logic
        selected_symptom_names = [
            SYMPTOM_MAPPING[sid]["name"] 
            for sid in selected_symptom_ids 
            if sid in SYMPTOM_MAPPING
        ]
        
        matching_diseases = []
        highest_match_percentage = 0
        risk_score = self.calculate_risk_score(selected_symptom_ids)
        
        user_symptoms_set = set(selected_symptom_names)
        
        for disease in processed_diseases:
            disease_symptoms_set = set(disease["symptoms"])
            common_symptoms = user_symptoms_set.intersection(disease_symptoms_set)
            
            match_score = len(common_symptoms)
            total_symptoms = len(disease_symptoms_set)
            
            if total_symptoms > 0:
                match_percentage = (match_score / total_symptoms) * 100
            else:
                match_percentage = 0
            
            if match_score > 0:
                disease_info = {
                    "id": disease["id"],
                    "name": disease["name"],
                    "match_percentage": round(match_percentage, 1),
                    "common_symptoms": list(common_symptoms),
                    "description": disease["description"],
                    "severity": disease["severity"],
                    "precautions": disease["precautions"],
                    "icon": disease["icon"]
                }
                matching_diseases.append(disease_info)
                
                if match_percentage > highest_match_percentage:
                    highest_match_percentage = match_percentage
        
        matching_diseases.sort(key=lambda x: (x["match_percentage"], x["severity"]), reverse=True)
        risk_level = self.determine_risk_level(risk_score, highest_match_percentage, matching_diseases)
        
        # Get exercise recommendations
        exercise_recommendations = self.get_exercises_by_risk_level(risk_level)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "matching_diseases": matching_diseases,
            "exercise_recommendations": exercise_recommendations,
            "selected_symptoms": [
                {"id": sid, "name": SYMPTOM_MAPPING[sid]["name"], "icon": SYMPTOM_MAPPING[sid]["icon"]}
                for sid in selected_symptom_ids if sid in SYMPTOM_MAPPING
            ]
        }
    
    def calculate_risk_score(self, selected_symptom_ids):
        """Calculate risk score"""
        base_score = 0
        high_severity_count = 0
        
        for symptom_id in selected_symptom_ids:
            if symptom_id in SYMPTOM_MAPPING:
                symptom = SYMPTOM_MAPPING[symptom_id]
                if symptom["severity"] == "High":
                    base_score += 3
                    high_severity_count += 1
                elif symptom["severity"] == "Medium":
                    base_score += 2
                else:
                    base_score += 1
        
        if high_severity_count >= 2:
            base_score += high_severity_count * 2
        
        return min(base_score, 10)
    
    def determine_risk_level(self, risk_score, highest_match_percentage, matching_diseases):
        """Determine risk level"""
        high_severity_diseases = [d for d in matching_diseases if d["severity"] == "High"]
        
        if (risk_score >= 8 or 
            highest_match_percentage >= 80 or 
            (len(high_severity_diseases) > 0 and highest_match_percentage >= 60)):
            return "high"
        elif (risk_score >= 5 or 
              highest_match_percentage >= 50 or 
              len(matching_diseases) >= 2):
            return "medium"
        else:
            return "low"

# Initialize components
user_manager = UserManager()
analyzer = SymptomAnalyzer()

# Initialize database before starting the app
# Database initialization will be handled in the main block below.

# Authentication Endpoints

@app.route('/api/auth/login', methods=['POST'])
def handle_login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get("user_id")
        password = data.get("password")
        
        if not user_id or not password:
            return jsonify({"success": False, "error": "User ID and password are required"}), 400
        
        # Authenticate user
        user = user_manager.authenticate_user(user_id, password)
        
        if user:
            # Remove password from response
            user_response = {k: v for k, v in user.items() if k != 'password'}
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": user_response
            })
        else:
            return jsonify({"success": False, "error": "Invalid User ID or password"}), 401
            
    except Exception as e:
        print(f"Error in login endpoint: {str(e)}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

@app.route('/api/auth/register', methods=['POST'])
def handle_register():
    """User registration endpoint - SIMPLIFIED VERSION"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        name = data.get("name", "").strip()
        age = data.get("age")
        gender = data.get("gender", "").strip()
        village = data.get("village", "").strip()
        
        print(f"Registration attempt: {name}, {age}, {gender}, {village}")
        
        if not name:
            return jsonify({"success": False, "error": "Name is required"}), 400
        if not age:
            return jsonify({"success": False, "error": "Age is required"}), 400
        if not gender:
            return jsonify({"success": False, "error": "Gender is required"}), 400
        if not village:
            return jsonify({"success": False, "error": "Village is required"}), 400

        # Validate age
        try:
            age = int(age)
            if age < 1 or age > 120:
                return jsonify({"success": False, "error": "Age must be between 1 and 120"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid age format"}), 400

        # Create user
        user_data = {
            "name": name, 
            "age": age, 
            "gender": gender, 
            "village": village,
            "mobile": data.get("mobile"), 
            "email": data.get("email")
        }
        
        user_id = user_manager.create_user(user_data)
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"Error in register endpoint: {str(e)}")
        return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 500

# User Profile Endpoint

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile with stats and history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user details
        cursor.execute('SELECT id, name, age, gender, village, mobile, email, created_at FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Get user stats
        stats = user_manager.get_user_stats(user_id)
        
        # Get user history
        history = user_manager.get_user_history(user_id)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "user": dict(user),
            "stats": stats or {},
            "history": history or []
        })
        
    except Exception as e:
        print(f"Error in user profile endpoint: {str(e)}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

# Analysis Endpoint

@app.route('/api/analyze', methods=['POST'])
def handle_analyze_request():
    """Analyze symptoms endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        name = data.get("name", "").strip()
        age = data.get("age")
        gender = data.get("gender", "").strip()
        village = data.get("village", "").strip()
        symptom_ids = data.get("symptoms", [])
        
        if not all([name, age, gender, village]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        if not symptom_ids:
            return jsonify({"success": False, "error": "No symptoms selected"}), 400

        # Validate age
        try:
            age = int(age)
            if age < 1 or age > 120:
                return jsonify({"success": False, "error": "Age must be between 1 and 120"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid age format"}), 400

        # Create/retrieve user
        user_data = {
            "name": name, "age": age, "gender": gender, "village": village,
            "mobile": data.get("mobile"), "email": data.get("email")
        }
        
        user_id = user_manager.create_user(user_data)
        
        # Perform analysis
        analysis_result = analyzer.analyze_symptoms(symptom_ids)
        
        # Save analysis to history
        analysis_id = user_manager.save_analysis(
            user_id, symptom_ids, analysis_result["risk_level"],
            analysis_result["risk_score"], analysis_result["matching_diseases"]
        )
        
        # Prepare response
        messages = {
            "high": "High risk detected! Please consult a healthcare professional immediately.",
            "medium": "Medium risk detected. Monitor your symptoms closely.",
            "low": "Low risk detected. Your symptoms don't indicate serious issues."
        }
        
        response = {
            "success": True,
            "user_id": user_id,
            "analysis_id": analysis_id,
            "risk_level": analysis_result["risk_level"],
            "risk_score": analysis_result["risk_score"],
            "message": messages.get(analysis_result["risk_level"]),
            "matching_diseases": analysis_result["matching_diseases"],
            "exercise_recommendations": analysis_result["exercise_recommendations"],
            "selected_symptoms": analysis_result["selected_symptoms"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

# Exercise Endpoint

@app.route('/api/exercises/<risk_level>', methods=['GET'])
def get_exercises(risk_level):
    """Get exercise recommendations by risk level"""
    try:
        if risk_level not in ['high', 'medium', 'low']:
            return jsonify({"success": False, "error": "Invalid risk level"}), 400
        
        exercises = analyzer.get_exercises_by_risk_level(risk_level)
        
        return jsonify({
            "success": True,
            "risk_level": risk_level,
            "exercises": exercises
        })
        
    except Exception as e:
        print(f"Error in exercises endpoint: {str(e)}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

# Debug Endpoints

@app.route('/api/debug/users', methods=['GET'])
def debug_users():
    """Debug endpoint to check all users in database"""
    try:
        users = user_manager.get_all_users()
        return jsonify({
            "success": True,
            "total_users": len(users),
            "users": users
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/debug/diseases', methods=['GET'])
def debug_diseases():
    """Debug endpoint to check diseases in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diseases ORDER BY id')
        diseases = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "total_diseases": len(diseases),
            "diseases": [dict(disease) for disease in diseases]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/debug/exercises', methods=['GET'])
def debug_exercises():
    """Debug endpoint to check exercises in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exercises ORDER BY risk_level, id')
        exercises = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "total_exercises": len(exercises),
            "exercises": [dict(exercise) for exercise in exercises]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"success": True, "message": "HealthShield API is running"})

if __name__ == '__main__':
    print("HealthShield API Server Starting...")
    print("Initializing HealthShield Database...")
    init_database()
    print("Database initialized successfully!")
    app.run(host='0.0.0.0', port=5000, debug=True)
