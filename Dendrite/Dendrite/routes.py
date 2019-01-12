# =========================================================LICENSE==============================================
'''
MIT License

Copyright (c) 2019 Manas Hejmadi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

THIS CODE IS WRITTEN BY MANAS M HEJMADI
'''
#==========================================================LICENSE================================================

from flask import render_template, url_for, flash, redirect, request, send_file
from Dendrite import app, db, bcrypt, generate_keypair
from Dendrite.forms import (RegistrationForm, LoginForm, CreateTender, CreateAsset, TransferAsset, RaiseTender)
from Dendrite.models import User, Contract, TransferRecord
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
import os
from Dendrite.bigchainuploader import BigChainUploader
import datetime

#GLOBAL STATE VARIABLES
# Define Global BigchainDB instance
bigchain = BigChainUploader()
filter_on = False
filter_ops = None
properties = []

# HELPER FUNCTIONS
# Change the status of the Contract
def change_status(c_id, func):
	if func == "ack":
		x = Contract.query.filter_by(contract_id=c_id).first()
		x.status = "Acknowledged"
		db.session.commit()
	elif func == "a":
		x = Contract.query.filter_by(contract_id=c_id).first()
		x.status = "Approved"
		all_contracts = Contract.query.filter_by(role=x.role).all()
		for y in all_contracts:
			os.remove(os.path.join(app.root_path, 'static\\Contracts', y.contract_file))
			db.session.delete(y)
		db.session.add(x)
		db.session.commit()
	elif func == "r":
		x = Contract.query.filter_by(contract_id=c_id).first()
		os.remove(os.path.join(app.root_path, 'static\\Contracts', x.contract_file))
		db.session.delete(x)
		db.session.commit()

# Create the Actual Tender and save it in the Database
def create_tender(form):
	filename = secure_filename(form.file.data.filename)
	form.file.data.save(f'Dendrite/static/Contracts/{filename}')
	# Creating the Database Object
	contract = Contract(contract_id=form.cid.data, contract_date=form.doi.data,
						contract_address=form.vendor_address.data, username=current_user.username, 
						role=current_user.role, contract_file=filename)
	db.session.add(contract)
	db.session.commit()
	flash(f"Contract '{form.cid.data}' created successfully!", 'success')

def create_genesis_asset(name, quantity, properties, contracts):
	asset = {}
	#Fill Asset Properties
	for p in properties:
		asset[(p.get('key')).replace(' ', '_')] = p.get('value')

	#Upload Data to BigChain
	bigchain.UploadData(asset, name, contracts, quantity, keys=current_user.keypair)
	#Create Genesis Block
	GenesisTransaction = bigchain.CreateGenesisBlock()
	#Check Status
	if(GenesisTransaction['Success']):
		flash(f"Successfully Deployed Asset '{name}'", "success")
		global prev_block, prev_output
		prev_block = GenesisTransaction['block']
		prev_output = GenesisTransaction['output']
	else:
		flash(f"Error occured while trying to Deploy Asset '{name}'", 'danger')
		print(f"====EXCEPTION====: {GenesisTransaction['Exception']}")

def transfertransaction():
	# Taking Global Variables
	global prev_block, prev_output
	if(current_user.role == "Manufacturer"):
		# Defining Owner and Recipient
		owner = current_user.keypair
		recipient = User.query.filter_by(role="Logistics", is_valid=True).first().keypair
		# Uploading Transfer Data to the Class
		bigchain.UploadTransferData(prev_block, prev_output, owner, recipient)
		# Sending Transaction
		Transfer = bigchain.TransferBlock()
		if(Transfer['Success']):
			flash(f"Successfully Transferred Asset from Manufacturer to Logistics.", "success")
			prev_block = Transfer['block']
			prev_output = Transfer['output']
	elif(current_user.role == "Logistics"):
		# Defining Owner and Recipient
		owner = current_user.keypair
		recipient = User.query.filter_by(role="Retailer", is_valid=True).first().keypair
		# Uploading Transfer Data to the Class
		bigchain.UploadTransferData(prev_block, prev_output, owner, recipient)
		# Sending Transaction
		Transfer = bigchain.TransferBlock()
		if(Transfer['Success']):
			flash(f"Successfully Transferred Asset from Manufacturer to Logistics.", "success")
			prev_block = Transfer['block']
			prev_output = Transfer['output']
	else:
		return redirect(url_for('homepage'))
	
# --------------------------------------------------------------------------------------------------------------------

# =================================================CORE PAGE ROUTES===============================================

@app.route("/login", methods=['GET', 'POST'])
def loginpage():	
	if current_user.is_authenticated:
		return redirect(url_for('homepage'))
	form = LoginForm()
	if form.validate_on_submit():
		role = dict(form.role.choices).get(form.role.data)
		user = User.query.filter_by(username=form.username.data, role=role).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			if role == "Vendor":
				return redirect(url_for('vendorpage'))
			elif role == "Company":
				return redirect(url_for('vendor_address'))
			elif role == "Manufacturer":
				return redirect(url_for('manufacturerpage'))
			elif role == "Logistics":
				return redirect(url_for('logisticspage'))
			elif role == "Retailer":
				return redirect(url_for('retailerpage'))
			else:
				return redirect(url_for('homepage'))
		else:
			flash('Invalid Credentials, Please try again', 'danger')
	return render_template("login.html", name='login', title="Dendrite - Login", form=form)

@app.route("/register", methods=['GET', 'POST'])
def registerpage():
	if current_user.is_authenticated:
		return redirect(url_for('homepage'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, role=(dict(form.role.choices).get(form.role.data)), password=hashed_password, keypair=generate_keypair())
		db.session.add(user)
		db.session.commit()
		flash(f"Account '{form.username.data}' created successfully!", 'success')
		return redirect(url_for('loginpage'))
	else:
		return render_template("register.html", name='register', title="Dendrite - Register", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('loginpage'))

# =================================================CORE PAGE ROUTES===============================================

# ===================================================OTHER ROUTES==================================================

# Home page
@app.route("/")
def homepage():
	return render_template('home.html', name='home', title='Dendrite - Home')

# Company Dashboard
@app.route("/tenders", methods=['GET', 'POST'])
@login_required
def vendor_address():
	contracts = Contract.query.all()
	form = RaiseTender()
	form.doi.data = datetime.datetime.now().strftime('%d-%m-%Y')
	if form.validate_on_submit():
		filename = secure_filename(form.file.data.filename)
		form.file.data.save(os.path.join(app.root_path, 'static/Contracts/CompanyContracts', filename))
		current_user.tender_request = filename
		db.session.commit()
		flash('Successfully Raised Tender', 'success')
		return redirect(url_for('vendor_address'))
	return render_template("companytender.html", name='company', title="Company Tender Management", contracts=contracts, form=form)

# Vendor Dashboard
@app.route("/vendor")
@login_required
def vendorpage():
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	return render_template("vendordashboard.html", name='vendor', title="Vendor Dashboard", contracts=contracts)

# Manufacturer Dashboard
@app.route("/manufacturer")
@login_required
def manufacturerpage():
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	return render_template("manufacturerdashboard.html", name='manufacturer', title="Manufacturer Dashboard", contracts=contracts)

# Logistics Dashboard
@app.route("/logistics")
@login_required
def logisticspage():
	transfer_rx = TransferRecord.query.filter_by(to_user=current_user.username, is_valid=False).first()
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	return render_template("logisticsdashboard.html", name='logistics', title="Logistics Dashboard", contracts=contracts, rx=transfer_rx)

# Retailer Dashboard
@app.route("/retailer")
@login_required
def retailerpage():
	transfer_rx = TransferRecord.query.filter_by(to_user=current_user.username, is_valid=False).first()
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	return render_template("retailerdashboard.html", name='retailer', title="Retailer Dashboard", contracts=contracts, rx=transfer_rx)

# Customer Check Origin Page
@app.route("/checkorigin", methods=['GET', 'POST'])
def checkorigin():
	return render_template("checkorigin.html", name='co', title="Check Origin")

#Transfer Asset Page
@app.route("/transferasset", methods=['GET', 'POST'])
@login_required
def transferassetpage():
	form = TransferAsset()
	if form.validate_on_submit():
		department = form.asset_name.data
		details = form.metadata.data
		bigchain.stage_metadata(details, department)
	return render_template("transferasset.html", name='ta', title="Transfer Asset", form=form)

# ===================================================OTHER ROUTES==================================================

# -------------------------------------------------FUNCTION BASED PAGES-----------------------------------------

@app.route("/createcontract", methods=['GET', 'POST'])
@login_required
def create_contract():
	form = CreateTender()
	form.doi.data = datetime.datetime.now().strftime('%d-%m-%Y')
	if form.validate_on_submit():
		# Uploading the Contract
		create_tender(form)
	return render_template("createtender.html", name='cc', title="Create Contract", form=form)

# Manufacturer Dashboard
@app.route("/checkrequests")
@login_required
def check_requests():
	role = current_user.role
	c = User.query.filter_by(role="Company").first()
	fn = c.tender_request
	if fn:
		file = os.path.join(app.root_path, 'static/Contracts/CompanyContracts', fn)
		return send_file(file)
	else:
		flash('No Tenders have been raised by the Company', 'danger')
		if role == "Vendor":
			return redirect(url_for('vendorpage'))
		elif role == "Manufacturer":
			return redirect(url_for('manufacturerpage'))
		elif role == "Logistics":
			return redirect(url_for('logisticspage'))
		elif role == "Retailer":
			return redirect(url_for('retailerpage'))


@app.route("/manufacturer/createasset", methods=['GET', 'POST'])
@login_required
def createasset():
	# ------------Getting all the Properties Posted by the Manufacturer----------
	global properties
	key = request.args.get('key')
	value = request.args.get('value')
	kvp = {
		'key': key,
		'value': value
	}
	if key and value not in ('', None, properties) and kvp not in properties:
		properties.append(kvp)
	# print(properties)
	# -----------------------End of Collecting Properties--------------------
	form = CreateAsset()
	if form.validate_on_submit():
		asset_name = form.asset_name.data
		quantity = form.quantity.data
		# print(asset_name)
		ctr_fnames = []
		for f in request.files.getlist('ctr'):
			ctr_fnames.append(secure_filename(f.filename))
		create_genesis_asset(asset_name, quantity, properties, ctr_fnames)
		return redirect(url_for('manufacturerpage'))
	return render_template("createassetpage.html", name='ca', title="Create Asset", p=properties, form=form)

@app.route("/deleteproperties", methods=['GET', 'POST'])
@login_required
def delete_all_properties():
	global properties
	properties = []
	return redirect(url_for('createasset'))

@app.route("/validate-transfer-request", methods=['GET', 'POST'])
@login_required
def validate_transfer_request():
	if(current_user.role == "Logistics"):
		logistics = Contract.query.filter_by(role="Logistics").first().username
		x = TransferRecord.query.filter_by(to_user=logistics).first()
		x.is_valid = True
		db.session.commit()
		return redirect(url_for('logisticspage'))
	elif(current_user.role == "Retailer"):
		retailer = Contract.query.filter_by(role="Retailer").first().username
		x = TransferRecord.query.filter_by(to_user=retailer).first()
		x.is_valid = True
		db.session.commit()
		return redirect(url_for('retailerpage'))
	else:
		return redirect(url_for('homepage'))

@app.route("/request_transfer", methods=['GET', 'POST'])
@login_required
def request_transfer():
	if(current_user.role == "Manufacturer"):
		logistics = Contract.query.filter_by(role="Logistics").first().username
		record = TransferRecord(from_user=current_user.username, to_user=logistics, 
								timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), is_valid=False)
		db.session.add(record)
		db.session.commit()
		flash('Asset Transfer will initiate after the Logistics Department acknowledges it', 'info')
		return redirect(url_for('manufacturerpage'))
	elif(current_user.role == "Logistics"):
		retailer = Contract.query.filter_by(role="Retailer").first().username
		record = TransferRecord(from_user=current_user.username, to_user=retailer, 
								timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), is_valid=False)
		db.session.add(record)
		db.session.commit()
		flash('Asset Transfer will initiate after the Retailer acknowledges it', 'info')
		return redirect(url_for('logisticspage'))
	return redirect(url_for('homepage'))
	
# -------------------------------------------------FUNCTION BASED PAGES-----------------------------------------

# -------------------------------------------CONTRACT DESCRIPTION CODE-----------------------------------------

# This is used to Display Each Individual Contract on the Description Panel for the Vendors page
@app.route("/vendors/<c_id>")
@login_required
def vendordesc(c_id):
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	c = Contract.query.filter_by(contract_id=c_id).first()
	return render_template("vendordashboard.html", name='vendor', title="Vendor Dashboard", contracts=contracts, cdesc=c)

# This is used to Display Each Individual Contract on the Description Panel for the Company Tenders
@app.route("/tenders/<c_id>")
@login_required
def contractdesc(c_id):
	# Checking Global value
	global filter_on
	global filter_ops
	if filter_on:
		contracts = Contract.query.filter_by(role=filter_ops).all()
	else:
		contracts = Contract.query.all()
	c = Contract.query.filter_by(contract_id=c_id).first()
	form = RaiseTender()
	return render_template("companytender.html", name='company', title="Company Tender Management", cdesc=c, contracts=contracts, form=form)

# This is used to Display Each Individual Contract on the Description Panel for the Manufacturers page
@app.route("/manufacturer/<c_id>")
@login_required
def manufacturerdesc(c_id):
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	c = Contract.query.filter_by(contract_id=c_id).first()
	return render_template("manufacturerdashboard.html", name='manufacturer', title="Manufacturer Dashboard", contracts=contracts, cdesc=c)

# This is used to Display Each Individual Contract on the Description Panel for the Retailers page
@app.route("/retailer/<c_id>")
@login_required
def retailerdesc(c_id):
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	c = Contract.query.filter_by(contract_id=c_id).first()
	return render_template("retailerdashboard.html", name='retailer', title="Retailer Dashboard", contracts=contracts, cdesc=c)

# This is used to Display Each Individual Contract on the Description Panel for the Retailers page
@app.route("/logistics/<c_id>")
@login_required
def logisticsdesc(c_id):
	contracts = Contract.query.filter_by(username=current_user.username, role=current_user.role)
	c = Contract.query.filter_by(contract_id=c_id).first()
	return render_template("logisticsdashboard.html", name='logistics', title="Logistics Dashboard", contracts=contracts, cdesc=c)

# -------------------------------------------CONTRACT DESCRIPTION CODE-----------------------------------------

# -------------------------------------------UPLOADING TENDER FROM SERVER--------------------------------------------
# Send Contract file from server
@app.route("/getcontract/<fn>")
def get_contract(fn):
	file = os.path.join(app.root_path, 'static/Contracts', fn)
	return send_file(file)

# -------------------------------------------UPLOADING TENDER FROM SERVER--------------------------------------------

#-------------------------------------------------FILTERING-----------------------------------------------

# This is used to filter the content
@app.route("/tenders/filterquery/<filter>")
@login_required
def filtervendor(filter):
	# Creating Global State variables
	global filter_on
	global filter_ops
	# Assigning them a value
	filter_on = True
	filter_ops = filter
	contracts = Contract.query.filter_by(role=filter).all()
	form = RaiseTender()
	return render_template("companytender.html", name='company', title="Company Tender Management", contracts=contracts, form=form)

# This is used to clear the filtered content
@app.route("/tenders/deletefilterquery")
@login_required
def deletefilters():
	# Reversing Global State value
	global filter_on
	global filter_ops
	filter_on = False
	filter_ops = ''
	return redirect(url_for('vendor_address'))

#--------------------------------------------------FILTERING-----------------------------------------------------

#---------------------------------------------CONTRACT LEVEL FUNCTIONS-----------------------------------------
@app.route("/tenders/<c_id>/<func>")
@login_required
def contractfunctions(c_id, func):
	global filter_on
	global filter_ops
	if current_user.role == "Company":
		# Checking Global value
		if filter_on:
			contracts = Contract.query.filter_by(role=filter_ops).all()
		else:
			contracts = Contract.query.all()
		# Change Status
		change_status(c_id, func)
		return redirect(url_for('vendor_address'))
	else:
		return "Route not accessible"
	c = Contract.query.filter_by(contract_id=c_id).first()
	return render_template("companytender.html", name='company', title="Company Tender Management", cdesc=c, contracts=contracts)

@app.route("/deletecontract/<c_id>")
@login_required
def deletecontract(c_id):
	contract = Contract.query.filter_by(contract_id=c_id).first()
	db.session.delete(contract)
	db.session.commit()
	# Delete Actual Contract from the Server
	os.remove(os.path.join(app.root_path, 'static\\Contracts', contract.contract_file))
	if current_user.role == "Vendor":
		return redirect(url_for('vendorpage'))
	elif current_user.role == "Manufacturer":
		return redirect(url_for('manufacturerpage'))
	elif current_user.role == "Retailer":
		return redirect(url_for('retailerpage'))
	elif current_user.role == "Logistics":
		return redirect(url_for('logisticspage'))
	
#---------------------------------------------CONTRACT LEVEL FUNCTIONS-----------------------------------------