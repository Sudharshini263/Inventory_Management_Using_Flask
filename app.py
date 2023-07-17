# app.py
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Database models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer, nullable=False)

    from_location_ref = db.relationship('Location', foreign_keys=[from_location])
    to_location_ref = db.relationship('Location', foreign_keys=[to_location])
    product_ref = db.relationship('Product')
    
    # app.py (continued)

# Views for Products
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product = Product(product_id=product_id)
        db.session.add(product)
        db.session.commit()

    products = Product.query.all()
    return render_template('products.html', products=products)

# Views for Locations
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_id = request.form['location_id']
        location = Location(location_id=location_id)
        db.session.add(location)
        db.session.commit()

    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

# Views for Product Movements
@app.route('/product_movements', methods=['GET', 'POST'])
def product_movements():
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        qty = int(request.form['qty'])
        
        product_ref = Product.query.filter_by(product_id=product_id).first()
        from_location_ref = Location.query.filter_by(location_id=from_location).first()
        to_location_ref = Location.query.filter_by(location_id=to_location).first()

        movement = ProductMovement(
            product_ref=product_ref,
            from_location_ref=from_location_ref,
            to_location_ref=to_location_ref,
            qty=qty
        )
        db.session.add(movement)
        db.session.commit()

    movements = ProductMovement.query.all()
    return render_template('product_movements.html', movements=movements)

# app.py (continued)

# View for Product Balances Report
@app.route('/report')
def report():
    locations = Location.query.all()
    products = Product.query.all()

    balance_grid = {}
    for product in products:
        balance_grid[product.product_id] = {}

        for location in locations:
            total_in = db.session.query(func.sum(ProductMovement.qty))\
                .filter(ProductMovement.product_id==product.product_id, ProductMovement.to_location==location.location_id)\
                .scalar()
            total_out = db.session.query(func.sum(ProductMovement.qty))\
                .filter(ProductMovement.product_id==product.product_id, ProductMovement.from_location==location.location_id)\
                .scalar()
            
            if not total_in:
                total_in = 0
                
            if not total_out:
                total_out = 0
                
            balance_grid[product.product_id][location.location_id] = abs(total_in - total_out)

    return render_template('report.html', locations=locations, products=products, balance_grid=balance_grid)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
