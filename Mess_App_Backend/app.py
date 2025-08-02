from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="web_ui")
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mess_stock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for items
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# --------- API Routes ---------

@app.route('/')
def home():
    return "<h2>Welcome to Mess Management API</h2>"

# Serve dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Get all stock items
@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit} for i in items])

# Add new item
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    new_item = Item(name=data["name"], quantity=data["quantity"], unit=data["unit"])
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item added successfully"})

# Use item (reduce quantity)
@app.route('/use_item', methods=['POST'])
def use_item():
    data = request.json
    item = Item.query.get(data["id"])
    if item:
        item.quantity -= data["quantity_used"]
        db.session.commit()
        return jsonify({"message": "Usage updated successfully"})
    return jsonify({"error": "Item not found"}), 404

# Delete item
@app.route('/delete_item', methods=['DELETE'])
def delete_item():
    data = request.json
    item = Item.query.get(data["id"])
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

# --- Extra Stats Route ---
@app.route('/stats', methods=['GET'])
def stats():
    total_members = 120
    todays_menu = ["Rice", "Dal", "Mixed Veg", "Salad"]
    meals_served_today = 350
    monthly_expenses = 55000
    return jsonify({
        "total_members": total_members,
        "todays_menu": todays_menu,
        "meals_served_today": meals_served_today,
        "monthly_expenses": monthly_expenses
    })

# Default stock (if DB empty)
with app.app_context():
    if Item.query.count() == 0:
        default_items = [
            {"name": "Rice", "quantity": 50, "unit": "kg"},
            {"name": "Dal", "quantity": 30, "unit": "kg"},
            {"name": "Wheat", "quantity": 40, "unit": "kg"},
            {"name": "Sugar", "quantity": 20, "unit": "kg"},
            {"name": "Tea Leaves", "quantity": 5, "unit": "kg"},
            {"name": "Cooking Oil", "quantity": 15, "unit": "liters"},
            {"name": "Salt", "quantity": 10, "unit": "kg"},
            {"name": "Milk", "quantity": 10, "unit": "liters"},
            {"name": "Potatoes", "quantity": 25, "unit": "kg"},
            {"name": "Onions", "quantity": 20, "unit": "kg"},
            {"name": "Tomatoes", "quantity": 15, "unit": "kg"},
            {"name": "Green Vegetables", "quantity": 10, "unit": "kg"},
            {"name": "Spices", "quantity": 5, "unit": "kg"}
        ]
        for item in default_items:
            db.session.add(Item(**item))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
