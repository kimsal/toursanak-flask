#!/usr/bin/env python
from database import *
import os.path as op
import os
import flask
from flask import json,abort,Flask,g, render_template,request,session,redirect,url_for,flash
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField,validators, ValidationError
from flask_sijax import sijax
from flask.json import jsonify
import math
from models import *
from forms import *
import atexit
# def sendEmail():
# 	print 'send email'
# sched = Scheduler()
# sched.add_interval_job(sendEmail, seconds=5)
# sched.start()

template ="template-2016"
config=""
email=''
password=''
with open('config.txt','r') as f:
	config=str(f.read())
	data=config.split('\n')
	template=data[0].split('"')[1]
	limit=int(data[1].split('"')[1])
	email=data[2].split('"')[1]
	pwd=data[3].split('"')[1]
########## End Configuration ############
#### send mail ####
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = email,
	MAIL_PASSWORD = pwd
	)
mail=Mail(app)
#####################
#Middleware
arr_header_image=['anakot.asea-1.jpg','anakot.asea-2.jpg','anakot.asea-3.jpg']
# header_image=random.choice (arr_header_image)
@app.context_processor
def inject_dict_for_all_templates():
    return dict(searchform=SearchForm(),header_image=random.choice (arr_header_image),logined_name=request.cookies.get('blog_name'),template_name= template,categories = Category.query.filter_by(is_menu=1),pages = Page.query.filter_by(is_menu=1),partners=Partner.query.order_by(Partner.id.desc()).all())
#========================================================
@auth.verify_token
def verify_token(token):
	user = UserMember.query.filter_by(email = request.cookies.get('blog_email'))
	if user.count()>0:
		for user_object in user:
			if user_object.verify_password(request.cookies.get('blog_password')):
				return True
	return False
@auth.error_handler
def goLoginPage():
	return redirect(url_for("admin_login"))
#================
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })
@app.route('/download/<name>')
def download(name=''):
	return send_file('static/files/'+name,
                     mimetype='text/csv',
                     attachment_filename=name,
                     as_attachment=True)
@app.route('/admin/login', methods=['POST', 'GET'])
@app.route('/admin/login/', methods=['POST', 'GET'])
def admin_login():
	form = UserMemberForm()
	if request.method == 'POST':
		email_form = request.form['email']
		password_form = request.form['password']
		user = UserMember.query.filter_by(email=email_form)
		if user.count()>0:
				#"set session"
				check=0
				for user_object in user:
					#return "{}".format(user_object.verify_password(password_form))
					if user_object.verify_password(password_form):
						response = make_response(redirect('/admin'))
						response.set_cookie("blog_id",str(user_object.id), expires=expire_date)
						response.set_cookie("blog_name",user_object.name, expires=expire_date)
						response.set_cookie("blog_email",user_object.email, expires=expire_date)
						response.set_cookie("blog_password",password_form, expires=expire_date)
						return response
					else:
						flash('Wrong user name or password !')
						return redirect(url_for("admin_login"))
		else:
			flash('Wrong user name or password !')
			return redirect(url_for("admin_login"))
	elif request.method == 'GET':
		#return str(request.cookies.get("blog_name"))
		if request.cookies.get("blog_name"):
			return redirect(url_for("admin_index"))
		return render_template('admin/form/login.html',form = form)
@app.route('/admin/logout', methods=['POST', 'GET'])
@app.route('/admin/logout/', methods=['POST', 'GET'])
# @auth.login_required
def logout():
	response = make_response(redirect('/'))
	response.set_cookie("blog_id","", expires=0)
	response.set_cookie("blog_name","", expires=0)
	response.set_cookie("blog_email","", expires=0)
	response.set_cookie("blog_password","", expires=0)
	return response
@app.route('/admin/register', methods=['POST', 'GET'])
@app.route('/admin/register/', methods=['POST', 'GET'])
#@auth.login_required
def admin_register():
	form = UserMemberForm()
	if request.method == 'POST':
		user=UserMember(request.form['name'],request.form['email'],request.form['password'])
		user.hash_password(request.form['password'])
		try:
			status=UserMember.add(user)
			if not status:
				flash("User Added successfully")
				return redirect(url_for('admin_login'))
			else:
				flash("Error in adding User !")
				return redirect(url_for('admin_register'))	
		except:
			flash("Error in adding User !")
			return redirect(url_for('admin_register'))
	return render_template('admin/form/register.html', form = form)
@app.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    form = PostForm()
    response = form.upload(endpoint=app)
    return response

########### member  ##########
@app.route('/admin/member', methods=['POST', 'GET'])
@app.route('/admin/member/', methods=['POST', 'GET'])
@app.route('/admin/member/<action>', methods=['POST', 'GET'])
@app.route('/admin/member/<action>/', methods=['POST', 'GET'])
@app.route('/admin/member/<action>/<slug>/', methods=['POST', 'GET'])
@app.route('/admin/member/<action>/<slug>', methods=['POST', 'GET'])
@app.route('/admin/member/pagin/<pagination>/')
@app.route('/admin/member/pagin/<pagination>')
@auth.login_required
def admin_member(pagination=1,action='',slug=''):
	form = MemberForm()
	if action=='add':
		#add event
		# return str(request.method)
		if request.method == 'GET':
			return render_template("admin/form/member.html",form=form)
		else:
			#try:
			filename=str(request.form['txt_temp_image'])
			member = Member(request.form['name'],request.form['possition'],request.form['detail'],filename)
        	# return str('event')
        	status = Member.add(member)
	        if not status:
	            flash("member added successfully")
	            return redirect(url_for('admin_member'))
	       	else:
	       		flash("Fail to add member !")
	       		return redirect(url_for('admin_member'))
		    # except Exception as e:
		    # 	flask(e.message)
		    # 	return redirect(url_for("admin_event"))
	elif action=='edit':
		#return 'update'+ slug
		members=Member.query.filter_by(slug=slug)
		if request.method == 'GET':
			return render_template("admin/form/member.html",form=form,member_object=members)
		else:
			try:
				members.update({"slug" : slugify(request.form['name']) , "name" : request.form['name'],'possition':request.form['possition'],'detail':request.form['detail'],'feature_image':request.form['txt_temp_image'] })
		   		status = db.session.commit()
				flash("Member updated successfully.")
				return redirect(url_for("admin_member"))
			except Exception as e:
				flash(e.message)
				return redirect(url_for("admin_member"))
	elif action=='delete':
		# return action+"...."
		try:
			member=Member.query.filter_by(slug=slug).first()
			status = Member.delete(member)
			flash('Member deleted successfully.')
			return redirect(url_for('admin_member'))
		except Exception as e:
			flash('Fail to delete member. '+ e.message)
			return redirect(url_for('admin_member'))
	else:
		members=Member.query.all()
		member=Member.query.order_by(Member.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Member.query.count())/limit)
		if((Member.query.count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template("admin/member.html",current_pagin=int(pagination),members=members,pagin=int(pagin))

############ End member ##########

#########  events  ######################
@app.route('/admin/event', methods=['POST', 'GET'])
@app.route('/admin/event/', methods=['POST', 'GET'])
@app.route('/admin/event/<action>', methods=['POST', 'GET'])
@app.route('/admin/event/<action>/', methods=['POST', 'GET'])
@app.route('/admin/event/<action>/<slug>/', methods=['POST', 'GET'])
@app.route('/admin/event/<action>/<slug>', methods=['POST', 'GET'])
@app.route('/admin/event/pagin/<pagination>/')
@app.route('/admin/event/pagin/<pagination>')
@auth.login_required
def admin_event(pagination=1,action='',slug=''):
	form = EventForm()
	if action=='add':
		#add event
		# return str(request.method)
		if request.method == 'GET':
			return render_template("admin/form/event.html",form=form)
		else:
			#try:
			filename=str(request.form['txt_temp_image'])
			event = Event(request.form['title'],request.form['description'],request.form['date'],filename,request.cookies.get('blog_id'))
        	# return str('event')
        	status = Event.add(event)
	        if not status:
	            flash("Event added was successfully")
	            return redirect(url_for('admin_event'))
	       	else:
	       		flash("Fail to add event !")
	       		return redirect(url_for('admin_event'))
		    # except Exception as e:
		    # 	flask(e.message)
		    # 	return redirect(url_for("admin_event"))
	elif action=='edit':
		#return 'update'+ slug
		events=Event.query.filter_by(slug=slug)
		if request.method == 'GET':
			return render_template("admin/form/event.html",form=form,events=events)
		else:
			try:
				events.update({"slug" : slugify(request.form['title']) , "title" : request.form['title'],'description':request.form['description'],'feature_image':request.form['txt_temp_image'],'date':request.form['date'] })
		   		status = db.session.commit()
				flash("Event updated successfully.")
				return redirect(url_for("admin_event"))
			except Exception as e:
				flash(e.message)
				return redirect(url_for("admin_event"))
	elif action=='delete':
		# return action+"...."
		try:
			event=Event.query.filter_by(slug=slug).first()
			status = Event.delete(event)
			flash('Deleted successful.')
			return redirect(url_for('admin_event'))
		except Exception as e:
			flash('Fail to delete event. '+ e.message)
			return redirect(url_for('admin_event'))
	else:
		events=Event.query.join(UserMember,Event.user_id == UserMember.id).order_by(Event.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Event.query.join(UserMember,Event.user_id == UserMember.id).count())/limit)
		if((Event.query.join(UserMember,Event.user_id == UserMember.id).count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template("admin/event.html",current_pagin=int(pagination),events=events,pagin=int(pagin))
#########  End events  ######################
############ Booking List ###################
@app.route('/admin/booking/')
@app.route('/admin/booking')
@app.route('/admin/booking/<action>/<name>')
@app.route('/admin/booking/<action>/<name>/')
@app.route('/admin/booking/<pagination>/')
@app.route('/admin/booking/<pagination>/')
@app.route('/admin/booking/<pagination>')
@app.route('/admin/booking/<pagination>/')
@auth.login_required
def admin_booking(pagination=1,action='',name=''):
	# return str(action)+":"+str(pagination)
	if action=='delete':		
		try:
			booking=Booking.query.filter_by(name=name).first()
			status = Booking.delete(booking)
			flash('Booking deleted successfully.')
			return redirect(url_for('admin_booking'))
		except Exception as e:
			flash('Fail to delete booking. '+ e.message)
			return redirect(url_for('admin_booking'))
	else:
		bookings=Booking.query.join(Post,Booking.post_id == Post.id).order_by(Booking.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Booking.query.join(Post,Booking.post_id == Post.id).count())/limit)
		if((Booking.query.join(Post,Booking.post_id == Post.id).count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template('admin/booking.html',bookings=bookings,current_pagin=int(pagination),pagin=int(pagin))

############ End Booking List ##########
# ############  Contact List ##########
@app.route('/admin/contact/')
@app.route('/admin/contact')
@app.route('/admin/contact/<action>/<firstname>')
@app.route('/admin/contact/<action>/<firstname>/')
@app.route('/admin/contact/<pagination>/')
@app.route('/admin/contact/<pagination>/')
@app.route('/admin/contact/<pagination>')
@app.route('/admin/contact/<pagination>/')
@auth.login_required
def admin_contact(pagination=1,action='',firstname=''):
	if action=='delete':		
		try:
			contact=Contact.query.filter_by(firstname=firstname).first()
			status = Contact.delete(contact)
			flash('Contact info deleted successful.')
			return redirect(url_for('admin_contact'))
		except Exception as e:
			flash('Fail to delete Contact info. '+ e.message)
			return redirect(url_for('admin_contact'))
	else:
		contacts=Contact.query.order_by(Contact.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Contact.query.count())/limit)
		if((Contact.query.count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template('admin/contact.html',contacts=contacts,current_pagin=int(pagination),pagin=int(pagin))

@app.route('/add/contact/<type_submit>/',methods=['POST'])
@app.route('/add/contact/<type_submit>',methods=['POST'])
def contact(type_submit=''):
	if type_submit=="":
		#by form refresh page
		return 'add and refresh page'
	elif type_submit=="ajax":
		#by ajax
		# return str(request.form['json_str']('firstname'))
		try:
			data=(request.form['json_str']).replace('"','')
			data=((data.split('[')[1]).split(']')[0]).split(',')
			firstname=data[0]
			lastname=data[1]
			email=data[2]
			check=Contact.query.filter_by(email=email)
			if check.count()>0:
				return 'email already exists.'
			else:
				contact=Contact(firstname,lastname,email)
				status = Contact.add(contact)
		        if not status:
		            return "Contact saved was successfully"
		       	else:
		       		return "Fail to add contact !"
		except Exception as e:
			return e.message
############ End Contact List ##########
############ Booking ####################
@app.route('/add/booking/<type_submit>/',methods=['POST'])
@app.route('/add/booking/<type_submit>',methods=['POST'])
@app.route('/add/booking/<type_submit>/<slug>/',methods=['POST'])
@app.route('/add/booking/<type_submit>/<slug>',methods=['POST'])
def booking(type_submit='',slug=''):
	if type_submit=="post":
		#by form refresh page
		posts=Post.query.filter_by(slug=slug)
		for post in posts:
			post_id=post.id
		booking = Booking(request.form['name'],request.form['email'],request.form['phone'],post_id,0,request.form['phone'])
		status = Booking.add(booking)
		if not status:
			flash("Booking added successfully")
			return redirect(url_for('index'))
		else:
			flash("Fail to add booking !")
       		return redirect(url_for('index'))
		return 'add and refresh page'
	elif type_submit=="ajax":
		#by ajax
		# return str(request.form['json_str']('firstname'))
		try:
			data=(request.form['json_str']).replace('"','')
			data=((data.split('[')[1]).split(']')[0]).split(',')
			name=data[0]
			email=data[1]
			phone=data[2]
			amount=data[3]
			post_id=data[4]
			detail=data[5]
			booking=Booking(name,email,phone,post_id,amount,detail)
			status = Booking.add(booking)
			if not status:
				return "Your info saved was successfully. We'll contact you soon."
			else:
				return "Fail to add booking !"
		except Exception as e:
			return e.message
############ End Booking ################
########### location  ##########
@app.route('/admin/location', methods=['POST', 'GET'])
@app.route('/admin/location/', methods=['POST', 'GET'])
@app.route('/admin/location/<action>', methods=['POST', 'GET'])
@app.route('/admin/location/<action>/', methods=['POST', 'GET'])
@app.route('/admin/location/<action>/<slug>/', methods=['POST', 'GET'])
@app.route('/admin/location/<action>/<slug>', methods=['POST', 'GET'])
@app.route('/admin/location/pagin/<pagination>/')
@app.route('/admin/location/pagin/<pagination>')
@auth.login_required
def admin_location(pagination=1,action='',slug=''):
	form = LocationForm()
	if action=='add':
		#add event
		# return str(request.method)
		if request.method == 'GET':
			return render_template("admin/form/location.html",form=form)
		else:
			#try:
			filename1=str(request.form['txt_temp_image'])
			filename2=str(request.form['txt_temp_image2'])
			location = Location(request.form['title'],request.form['address'],request.form['hour'],request.form['contact'],filename1,filename2,request.cookies.get('blog_id'))
        	# return str('event')
        	status = Location.add(location)
	        if not status:
	            flash("Location added successfully")
	            return redirect(url_for('admin_location'))
	       	else:
	       		flash("Fail to add location !")
	       		return redirect(url_for('admin_location'))
		    # except Exception as e:
		    # 	flask(e.message)
		    # 	return redirect(url_for("admin_event"))
	elif action=='edit':
		#return 'update'+ slug
		locations=Location.query.filter_by(slug=slug)
		if request.method == 'GET':
			return render_template("admin/form/location.html",form=form,location_object=locations)
		else:
			try:
				locations.update({"slug" : slugify(request.form['title']) , "title" : request.form['title'],'address':request.form['address'],'hour':request.form['hour'],'contact':request.form['contact'],'feature_image1':request.form['txt_temp_image'],'feature_image2':request.form['txt_temp_image2'] })
		   		status = db.session.commit()
				flash("Location updated successfully.")
				return redirect(url_for("admin_location"))
			except Exception as e:
				flash(e.message)
				return redirect(url_for("admin_location"))
	elif action=='delete':
		# return action+"...."
		try:
			location=Location.query.filter_by(slug=slug).first()
			status = Location.delete(location)
			flash('location deleted successfully.')
			return redirect(url_for('admin_location'))
		except Exception as e:
			flash('Fail to delete location. '+ e.message)
			return redirect(url_for('admin_location'))
	else:
		locations=Location.query.all()
		location=Location.query.order_by(Location.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Location.query.count())/limit)
		if((Location.query.count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template("admin/location.html",current_pagin=int(pagination),locations=locations,pagin=int(pagin))

############ End location ##########

############ Partner  ##########
@app.route('/admin/partner', methods=['POST', 'GET'])
@app.route('/admin/partner/', methods=['POST', 'GET'])
@app.route('/admin/partner/<action>', methods=['POST', 'GET'])
@app.route('/admin/partner/<action>/', methods=['POST', 'GET'])
@app.route('/admin/partner/<action>/<slug>/', methods=['POST', 'GET'])
@app.route('/admin/partner/<action>/<slug>', methods=['POST', 'GET'])
@app.route('/admin/partner/pagin/<pagination>/')
@app.route('/admin/partner/pagin/<pagination>')
@auth.login_required
def admin_partner(pagination=1,action='',slug=''):
	form = PartnerForm()
	if action=='add':
		#add event
		# return str(request.method)
		if request.method == 'GET':
			return render_template("admin/form/partner.html",form=form)
		else:
			#try:
			filename=str(request.form['txt_temp_image'])
			partner = Partner(request.form['name'],request.form['url'],filename)
        	# return str('event')
        	status = Partner.add(partner)
	        if not status:
	            flash("Partner added was successfully")
	            return redirect(url_for('admin_partner'))
	       	else:
	       		flash("Fail to add partner !")
	       		return redirect(url_for('admin_partner'))
		    # except Exception as e:
		    # 	flask(e.message)
		    # 	return redirect(url_for("admin_event"))
	elif action=='edit':
		#return 'update'+ slug
		partners=Partner.query.filter_by(slug=slug)
		if request.method == 'GET':
			return render_template("admin/form/partner.html",form=form,partner_object=partners)
		else:
			try:
				partners.update({"slug" : slugify(request.form['name']) , "name" : request.form['name'],'url':request.form['url'],'feature_image':request.form['txt_temp_image'] })
		   		status = db.session.commit()
				flash("Partner updated successfully.")
				return redirect(url_for("admin_partner"))
			except Exception as e:
				flash(e.message)
				return redirect(url_for("admin_partner"))
	elif action=='delete':
		# return action+"...."
		try:
			partner=Partner.query.filter_by(slug=slug).first()
			status = Partner.delete(partner)
			flash('Partner deleted successfully.')
			return redirect(url_for('admin_partner'))
		except Exception as e:
			flash('Fail to delete partner. '+ e.message)
			return redirect(url_for('admin_partner'))
	else:
		partners=Partner.query.order_by(Partner.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
		pagin=math.ceil((Partner.query.count())/limit)
		if((Partner.query.count())%limit != 0 ):
			pagin=int(pagin+1)
		return render_template("admin/partner.html",current_pagin=int(pagination),partners=partners,pagin=int(pagin))

############ End Partner ##########
@app.route('/admin')
@app.route('/admin/post')
@app.route('/admin/')
@app.route('/admin/<pagination>')
@auth.login_required
def admin_index(pagination=1):
	posts=Post.query.join(Category,Post.category_id == Category.id).order_by(Post.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
	pagin=math.ceil((Post.query.join(Category,Post.category_id == Category.id).count())/limit)
	if((Post.query.count())%limit != 0 ):
		pagin=int(pagin+1)
	return render_template('admin/index.html' , posts = posts , pagin = int(pagin) , current_pagin = int(pagination))


@app.route('/admin/post/add', methods = ['GET', 'POST'])
@app.route('/admin/post/add/', methods = ['GET', 'POST'])
@app.route('/admin/post/edit/<slug>', methods = ['GET', 'POST'])
@app.route('/admin/post/edit/<slug>/', methods = ['GET', 'POST'])
@auth.login_required
def admin_post_add(slug=""):
	form = PostForm()
	categories = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
	form.category_id.choices = categories
	if request.method == 'POST':
		try:
			if form.validate() == False:
		   		flash('Please try to fill form again.')
		   		return redirect(url_for('admin_post_add'))
		   	else:
		   		obj=Post.query.filter_by(slug=slug)
		   		for post in obj:
		   			old_images=post.images
		   		now = str(datetime.now())
				now= now.replace(':',"",10).replace(' ','',4).replace('.','',5).replace('-','',5)
		   		result = request.form
				filename=str(request.form['txt_temp_image'])
				# return filename
				if not slug:
		   			if file:
		   				images=''
		   				help=1
	   					uploaded_files = flask.request.files.getlist("other_image[]")
		   				# return filename
		   				for f in uploaded_files:
		   					imagename = secure_filename(f.filename)
		   					if imagename!="":
			   					f.save(os.path.join(app.config['UPLOAD_FOLDER'], now+"-"+imagename))
			   					if help==1:
			   						images=now+"-"+imagename
			   					else:
			   						images=images+"$$$$$"+(now+"-"+imagename)
			   					help=help+1
			   			if request.form["price"]=="":
			   				price=0
			   			else:
			   				price=int(request.form["price"])
			   			
		   				obj=Post(request.form['title'],request.form['description'],request.form['category_id'],filename,request.cookies.get('blog_id'),0,images,price,request.form["map"],request.form["short_description"])
			        	status=Post.add(obj)
				        if not status:
				            flash("Post added successfully")
				            return redirect(url_for('admin_index'))
				        else:
				        	flash("Fail to add post !")
				        	return redirect(url_for('admin_post_add'))
				elif slug:
					# return str(request.form["image1"])
		   			if not not file: 
		   				images=''
		   				help=1
	   					uploaded_files = flask.request.files.getlist("other_image[]")
		   				# return filename
		   				
		   				for f in uploaded_files:
		   					imagename = secure_filename(f.filename)
		   					if imagename!="":
			   					f.save(os.path.join(app.config['UPLOAD_FOLDER'], now+"-"+imagename))
			   					if help==1:
			   						images=now+"-"+imagename
			   					else:
			   						images=images+"$$$$$"+(now+"-"+imagename)
			   					help=help+1
			   			if old_images!='':
				   			if images!='':
				   				images=old_images+"$$$$$"+images
				   			else:
				   				images=old_images
			   			#keep old other images

				   		for post in obj:
				   			old_images=post.images
				   		arr_to_remove=(request.form['all_removed_images']).split("$$$$$")
				   		for item in arr_to_remove:
				   			images=images.replace(item,'')
				   		images=images.replace('$$$$$$$$$$','$$$$$')
				   		#end keep old images
				   		# return old_images
	   					obj.update({"slug" : slugify(request.form['title']) , "title" : request.form['title'],'description':request.form['description'],"category_id":request.form['category_id'],'feature_image':filename,'images':images,'price':request.form["price"],'short_description':request.form["short_description"],'map':request.form["map"] })
	   					status = db.session.commit()
		   				if not status:
		   					flash("Post updated successfully")
		   					return redirect(url_for('admin_index'))
		   			for post in obj:
		   				tempFileName=post.feature_image
	   				filename=tempFileName
	   				obj.update({"slug" : slugify(request.form['title']) , "title" : request.form['title'],'description':request.form['description'],'category_id':request.form['category_id'],'feature_image':filename })
	   				status = db.session.commit()
	   				if not status:
	   					flash("Post updated was successfully")
	   					return redirect(url_for('admin_index'))
			        else:
			        	flash("Fail to update post!")
			        	return redirect(url_for('admin_index'))
		except Exception  as e:
			flash(str(e.message))
			return redirect(url_for("admin_post_add"))
	elif request.method == 'GET':
		if slug:
			post=Post.query.filter_by(slug=slug)
			return render_template('admin/form/post.html', post = post, form = form)
		else:
			return render_template('admin/form/post.html', form = form)
@app.route('/admin/category', methods = ['GET', 'POST'])
@app.route('/admin/category/', methods = ['GET', 'POST'])
@app.route('/admin/category/add', methods = ['GET', 'POST'])
@app.route('/admin/category/add/', methods = ['GET', 'POST'])
@app.route('/admin/category/edit/<slug>', methods = ['GET', 'POST'])
@app.route('/admin/category/edit/<slug>/', methods = ['GET', 'POST'])
@auth.login_required
def admin_category_add(slug=""):
	form = CategoryForm()
	categories= Category.query.order_by(Category.name)
	if request.method == 'POST':
		try:
			if form.validate() == False:
		   		flash('please input category name !')
		   		return redirect(url_for('admin_category_add'))
	   		if not slug:
	   			#add category
		   		obj=Category(request.form['name'])
		   		status=Category.add(obj)
				if not status:
					flash("Category Added successfully")
					return redirect(url_for('admin_category_add'))
				else:
					flash("Error in adding page !")
					return redirect(url_for('admin_category_add'))	
			elif slug:
				#update category
	   			Category.query.filter_by(slug = slug).update({"slug" : slugify(request.form['name']) , "name" : request.form['name'] })
	   			status = db.session.commit()
	   			if not status:
	   				flash("Category updated successfully")
	   				return redirect(url_for('admin_category_add'))
		        else:
		        	flash("Error in updating category !")
		        	return redirect(url_for('admin_category_add'))
		except Exception as e:
			flash(str(e.message))
			return redirect(url_for("admin_category_add"))
	elif request.method == 'GET':
		if not slug:
			return render_template('/admin/form/category.html',categories=categories, form = form)
		else:
			cat= Category.query.filter_by(slug=slug)
			return render_template('/admin/form/category.html',categories=categories,cat=cat, form = form)
@app.route('/admin/page/')
@app.route('/admin/page')
@app.route('/admin/page/<pagination>')
@auth.login_required
def admin_page(pagination=1):
	pages = Page.query.order_by(Page.id.desc())
	return render_template('admin/page.html', pages=pages)
@app.route('/admin/page/add', methods = ['GET', 'POST'])
@app.route('/admin/page/add/', methods = ['GET', 'POST'])
@app.route('/admin/page/edit/<slug>/', methods = ['GET', 'POST'])
@app.route('/admin/page/edit/<slug>', methods = ['GET', 'POST'])
@auth.login_required
def admin_page_add(slug=''):
	form = PageForm()
	if request.method == 'POST':
		try:
			if form.validate() == False:
		   		flash('Please try to fill form again !'	)
		   		return redirect(url_for('admin_page_add'))
		   	else:
		   		if not slug:
		   			#add new
			   		obj=Page(request.form['title'],request.form['description'])
			   		status=Page.add(obj)
					if not status:
						flash("Page Added successfully")
						return redirect(url_for('admin_page'))
					else:
						flash("Error in adding page !")
						return redirect(url_for('admin_page_add'))
		   		elif slug:
		   			Page.query.filter_by(slug = slug).update({"slug" : slugify(request.form['title']) , "title" : request.form['title'] , "description" : request.form['description']})
		   			status = db.session.commit()
		   			if not status:
		   				flash("Page updated successfully")
		   				return redirect(url_for('admin_page'))
			        else:
			        	flash("Error !")
			        	return redirect(url_for('admin_page_add'))
		except Exception as e:
			flash(str(e.message))
			return redirect(url_for("admin_page_add"))
	else:
		if not slug:
			return render_template('/admin/form/page.html', form = form)
		else:
			page= Page.query.filter_by(slug=slug)
			return render_template('/admin/form/page.html',page=page, form = form)
@app.route('/admin/page/delete/<slug>/')
@app.route('/admin/page/delete/<slug>')
@auth.login_required
def admin_page_delete(slug=''):
	obj1 = Page.query.filter_by(slug=slug).first()
	try:
		status = Page.delete(obj1)
		flash('Deleted successful.')
		return redirect(url_for('admin_page'))
	except:
		flash('Fail to delete !')
		return redirect(url_for('admin_page'))
@app.route('/admin/category/delete/<slug>')
@app.route('/admin/category/delete/<slug>/')
@auth.login_required
def admin_category_delete(slug):	
	obj1 = Category.query.filter_by(slug=slug).first()
	try:
		status = Category.delete(obj1)
		flash('Deleted successful.')
		return redirect(url_for('admin_category_add'))
	except:
		flash('Fail to delete !')
		return redirect(url_for('admin_category_add'))

@app.route('/admin/post/delete/<slug>')
@app.route('/admin/post/delete/<slug>/')
@auth.login_required
def admiin_post_delete(slug=''):
	obj = Post.query.filter_by(slug=slug).first()
	try:
		status = Post.delete(obj)
		flash('Post deleted successful.')
		return redirect(url_for('admin_index'))
	except Exception as e:
		flash(str(e.message))
		return redirect(url_for('admin_index'))
@app.route('/admin/template')
@app.route('/admin/template/')
@auth.login_required
def admin_template():
	templates_dir=os.listdir(os.path.join(app.template_folder))
	templates_dir.remove("admin")
	return render_template("/admin/template.html",templates_dir=templates_dir)
@app.route('/admin/template/<new_template>')
@app.route('/admin/template/<new_template>/')
def admin_choose_template(new_template):
	try:
		global config
		global template
		global limit
		global email
		with open('config.txt','w') as f:
			config=config.replace(template,new_template)
			f.write(config)
		###Read again:
		with open('config.txt','r') as f:
			config=str(f.read())
			data=config.split('\n')
			template=data[0].split('"')[1]
			limit=int(data[1].split('"')[1])
			email=data[2].split('"')[1]
			pwd=data[3].split('"')[1]
		flash("Template changed successfully.")
	except Exception as e:
		flash(str(e.message))
	return redirect(url_for('admin_index'))
@app.route('/admin/limit')
@app.route('/admin/limit/')
@app.route('/admin/limit/<number>', methods=['POST','GET'])
@app.route('/admin/limit/<number>/', methods=['POST','GET'])
def admin_limit(number=0):
	global config
	global template
	global limit
	global email
	if number==0:
		return render_template('/admin/limit.html',limit=limit)
	else:
		try:
			#return config
			with open('config.txt','w') as f:
				config=config.replace('limit="'+str(limit)+'"','limit="'+str(number)+'"')
				f.write(str(config))
			###Read again:
			with open('config.txt','r') as f:
				config=str(f.read())
				data=config.split('\n')
				template=data[0].split('"')[1]
				limit=int(data[1].split('"')[1])
				email=data[2].split('"')[1]
				pwd=data[3].split('"')[1]
			return jsonify({'success':"Ok" })
		except Exception as e:
			return jsonify({'success':str(e.message) })
@app.route('/admin/social')
@app.route('/admin/social/')
def admin_social():
	return render_template('/admin/social.html')
@app.route('/admin/menu')
@app.route('/admin/menu/')
def admin_menu(id=0,value=0):
	if request.method == 'GET':
		ps=Page.query.all()
		cats=Category.query.all()
		return render_template('/admin/menu.html',ps=ps,cats=cats)
@app.route('/admin/menu/<id>/<value>/<model>', methods=['POST', 'GET'])
@app.route('/admin/menu/<id>/<value>/<model>/', methods=['POST', 'GET'])
def admin_menu_set(id=0,value=0,model=''):
		if model=='category':
			try:
				category_object=Category.query.filter_by(id=id)
				category_object.update({"is_menu" : value })
				status = db.session.commit()
				if not status:
					return jsonify({'success':True}) 
				else:
					return jsonify({'success':False})
			except Exception as e:
				return jsonify({'success':str(e.message) })
		elif model=='page':
			try:
				page_object=Page.query.filter_by(id=id)
				page_object.update({"is_menu" : value })
				status = db.session.commit()
				if not status:
					return jsonify({'success':True}) 
				else:
					return jsonify({'success':False})
			except Exception as e:
				return jsonify({'success':str(e.message) })
@app.route('/recovery',methods=["POST","GET"])
@app.route('/recovery/',methods=["POST","GET"])
def verify_email():
	if request.method=="GET":
		return render_template('admin/verify-email.html')
	else:
		your_passowrd=''
		email_temp=request.form['email']
		users=UserMember.query.filter_by(email=email_temp)
		for usr in users:
			your_passowrd=usr.password2
			your_name=usr.name
		if your_passowrd!="":
			#send email
			try:
				global email
				#return email+":"+email_temp+":"+pwd
				msg = Message('Password recovery',sender=email,recipients=[email_temp])
				message_string='<div style="width:400px;border:2px solid blue;padding:10px;">Hello '+your_name+',<br/> Your password is: <b>'+your_passowrd+'</b></b> Thanks for choosing Amogli service.<br/></div>'
				msg.html = message_string
				mail.send(msg)				
				flash("Please check your email to recovery the password.")
				return redirect(url_for("admin_login"))
			except Exception as e:
				raise
				return str(e.message)
		else:
			#wrong email
			flash("Sorry, We couldn't find this email to recovery you password. It might wrong email address")
			return render_template('admin/verify-email.html')
			return "We couldn't find this email."
###########SEND MAIL##############
@app.route('/admin/email/group', methods = ['GET', 'POST'])
@app.route('/admin/email/group/', methods = ['GET', 'POST'])
# @app.route('/admin/email/group/<slug>', methods = ['GET', 'POST'])
# @app.route('/admin/email/group/<slug>/', methods = ['GET', 'POST'])
@app.route('/admin/email/group/<slug>/<action>', methods = ['GET', 'POST'])
@app.route('/admin/email/group/<slug>/<action>/', methods = ['GET', 'POST'])
@auth.login_required
def admin_mail_group(slug='',action=''):
	#slug is group name
	form = GroupForm()
	groups=Group.query.order_by(Group.published_at.desc()).all()
	if slug=='':
		if request.method=="GET":
			return render_template("admin/form/mailgroup.html",name=slug,form=form,groups=groups)
		else:
			try:
				name = request.form['name']
				grp=Group(name)
				status=Group.add(grp)
				if not status:
					flash("Group Added successfully")
					return redirect(url_for('admin_mail_group'))
				else:
					flash("Error in adding Group !")
					return redirect(url_for('admin_mail_group'))
			except Exception as e:
				flask(e.message)
				return redirect(url_for("admin_mail_group"))
	else:
		#edit or delete
		if action=="edit":
			if request.method=="GET":
				return render_template("admin/form/mailgroup.html",form=form,groups=groups,name=slug)
			else:
				try:
					obj=Group.query.filter_by(name=slug)
					obj.update({"name" : request.form['name'] })
					status = db.session.commit()
					#status = obj.update({"name":request.form['name']})
					if not status:
						flash("Group updated successfully")
						return redirect(url_for('admin_mail_group'))
					else:
						flash("Error in updating group !")
						return redirect(url_for('admin_mail_group'))
				except Exception as e:
					flash(e.message)
					return redirect(url_for("admin_mail_group"))
		else:
			#delete group
			try:
				obj=Group.query.filter_by(name=slug).first()
				status = Group.delete(obj)
				if not status:
					flash("Group deleted successfully")
					return redirect(url_for('admin_mail_group'))
				else:
					flash("Error in deleting group !")
					return redirect(url_for('admin_mail_group'))
			except Exception as e:
				flash(e.message)
				return redirect(url_for('admin_mail_group'))
@app.route('/admin/mail', methods = ['GET', 'POST'])
@app.route('/admin/mail/', methods = ['GET', 'POST'])
@auth.login_required
def admin_mail():
	if request.method=="GET":
		emails=Email.query.order_by(Email.id.desc())
		groups=Group.query.order_by(Group.id.desc())
		return render_template("admin/form/maillist.html",groups=groups,emails=emails)
	else:
		obj=Email(request.form['email'],request.form['name'])
   		status=Email.add(obj)
		if not status:
			flash("Email added successfully")
			return redirect(url_for('admin_mail'))
		else:
			flash("Error in adding email !")
			return redirect(url_for('admin_mail'))	
	
		return redirect(url_for('admin_mail'))
email_count=0
subject=''
description=''
def sendEmail():
	print 'send email here'
	global email_count
	email_count=email_count+1

@app.route('/admin/email', methods = ['GET', 'POST'])
@app.route('/admin/email/', methods = ['GET', 'POST'])
@auth.login_required
def admin_email():
	if request.method=="GET":
		groups=Group.query.order_by(Group.id.desc())
		return render_template("admin/form/sendmail.html",groups=groups)
	else:
		global subject
		global description
		subject = request.form['subject']
		description = request.form['detail']
		groups = request.form['groups']
		sched = Scheduler()
		sched.add_interval_job(sendEmail, seconds=5)
		sched.start()
		return redirect(url_for("admin_email"))
@app.route('/admin/earn')
@app.route('/admin/earn/')
def admin_earn():
	return render_template("admin/earn.html")
@app.route('/admin/search')
@app.route('/admin/search/')
@app.route('/admin/search/<pagination>')
@app.route('/admin/search/<pagination>/')
def admin_search(pagination=1):
	global limit
	search=(str(request.args['q']))#.split()
	search=search.replace(" ",'+')
	#return search
	if search=="":
		return redirect(url_for("admin_index"))
	# query_result=(Post.query.filter((Post.title).match("'%"+search+"%'"))).count()
	posts=Post.query.filter((Post.title).match("'%"+search+"%'")).all()#limit(limit).offset(int(int(int(limit)-1)*limit))
	pagin=math.ceil((Post.query.filter((Post.title).match("'%"+search+"%'")).count())/limit)
	#return str((posts))
	if math.ceil(pagin)%limit != 0:
		pagin=int(pagin+1)
	#return str(pagin)
	return render_template('admin/search.html',search=search,page_name='search',posts=posts,current_pagin=int(pagination),pagin=(int(pagin)))
############## End send mail #####################
######### Personalize Email ###########
@app.route('/admin/checkemail/<email_id>/<group_id>/<action>/', methods=['POST', 'GET'])
@app.route('/admin/checkemail/<email_id>/<group_id>/<action>', methods=['POST', 'GET'])
def check_email(email_id,group_id,action):
	email_id=int(email_id)
	group_id=int(group_id)
	if action=="check":
		obj=Emailgroup.query.filter_by(email_id=email_id).filter_by(group_id=group_id)
		if obj.count()>0:
			return jsonify({'status':True })
		return jsonify({'status':False })
	elif action=="remove":
		obj=Emailgroup.query.filter_by(email_id=email_id).filter_by(group_id=group_id).first()
		Emailgroup.delete(obj)
		return jsonify({'status':'success'})
	elif action=="add":
		emailgroup = Emailgroup(email_id,group_id)
    	status = Emailgroup.add(emailgroup)
        if not status:
            return jsonify({'status':'success' })
       	else:
       		return jsonify({'status':'fail' })
#############End personalize email####################
#End Middleware
#client
@app.errorhandler(404)
def page_not_found(e):
	return render_template(template+"/404.html")
@app.route('/')
@app.route('/pagin/<pagination>/')
@app.route('/pagin/<pagination>')
def index(pagination=1):
	global limit
	form=ContactForm() 
	slide=Post.query.join(Category).filter(Category.name=="TOUR").order_by(Post.id.desc()).limit(1)
	posts_top = Post.query.join(UserMember).join(Category).filter(Category.name=="TOUR").order_by(Post.id.desc()).limit(9).offset(1)
	posts_bottom = Post.query.join(UserMember).join(Category).filter(Category.name=="ACTIVITIES").order_by(Post.id.desc()).limit(9)
	home_posts=Post.query.join(UserMember).order_by(Post.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
	pagin=math.ceil((Post.query.count())/limit)
	locations=Location.query.order_by(Location.id.desc()).all()
	events=Event.query.order_by(Event.id.desc()).all()
	members=Member.query.order_by(Member.id.desc()).all()
	return render_template(template+'/index.html',slide=slide,members=members,events=events,locations=locations,form=form,page_name='home',posts_top=posts_top,home_posts=home_posts,posts_bottom = posts_bottom,pagin=int(pagin),current_pagin=int(pagination))

@app.route('/booking/<slug>')
@app.route('/booking/<slug>/')
def booking_page(slug):
	form=BookingForm()
	post=Post.query.filter_by(slug=slug)
	for p in post:
		post_id=p.id
		post_title=p.title
	return render_template(template+'/booking.html',post_title=post_title,post_id=post_id,form=form,slug=slug,page_name='booking')
@app.route('/<slug>')
@app.route('/<slug>/')
@app.route('/<slug>/<pagination>')
@app.route('/<slug>/<pagination>/')
#can be single and category page
def single(slug='',pagination=1):
	# session.clear()
	# return 'd'
	form=BookingForm()
	try:
		location=Location.query.filter_by(slug=slug)
		if location.count()>0:
			return render_template(template+'/location.html',page_name='location',form=form,location_object=location)

		event=Event.query.filter_by(slug=slug)
		if event.count()>0:
			return render_template(template+'/event.html',page_name='event',event_object=event)

		post_object=Post.query.filter_by(slug=slug)#.limit(1)
		if post_object.count()<=0:
			page_object=Page.query.filter_by(slug=slug)#.limit(1)
		if post_object.count()>0:
			#add views count
			if session.get('amoogli_view') ==None:
				session['amoogli_view']=' '
				# return str(slug in str(session.get('amoogli_view')))
			if not slug in str(session.get('amoogli_view')):
				for post in post_object:
					old_view = post.views
					post_object.update({"views" : (old_view+1) })
					status = db.session.commit()
					session['amoogli_view'] = (str(session.get('amoogli_view')))+","+slug
		elif page_object.count()>0:
			members=Member.query.order_by(Member.id.desc()).all()
			return render_template(template+"/page.html",members=members,page_name="page",page_object=page_object)
		else:
			category=Category.query.filter_by(slug=slug)
			if category.count()>0:
				cat_id=""
				category_name="None"
				category_slug=""
				for cat in category:
					cat_id=cat.id
					category_name=cat.name
					category_slug=cat.slug
				if cat_id == "":
					abort(404)
				posts=Post.query.filter_by(category_id=cat_id).order_by(Post.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
				pagin=math.ceil((Post.query.filter_by(category_id=cat_id).count())/limit)
				if(math.ceil(Post.query.filter_by(category_id=cat_id).count())%limit != 0 ):
					pagin=int(pagin+1)
				#return str(limit)
				if category_name=='Blog':
					return render_template(template+'/blog.html',page_name='category',category_slug=category_slug,category_name=category_name,posts=posts,pagin=int(pagin),current_pagin=int(pagination))
				return render_template(template+'/category.html',page_name='category',category_slug=category_slug,category_name=category_name,posts=posts,pagin=int(pagin),current_pagin=int(pagination))
			
	except Exception as e:
		return str(e.message)
		abort(404)
	cat_id=0
	post_object=Post.query.join(Category,Post.category_id == Category.id).filter(Post.slug==slug)
	for post in post_object:
		cat_id=post.category_id
	related_posts=Post.query.filter_by(category_id=cat_id).order_by(Post.id.desc()).limit(3)
	events=Event.query.all()
	return render_template(template+'/single.html',events=events,form=form,page_name='single',related_posts=related_posts,post_object=post_object)
@app.route('/category/<slug>')
@app.route('/category/<slug>/')
@app.route('/category/<slug>/<pagination>')
@app.route('/category/<slug>/<pagination>')
def category(slug='',pagination=1):
	category=Category.query.filter_by(slug=slug)
	cat_id=""
	category_name="None"
	category_slug=""
	for cat in category:
		cat_id=cat.id
		category_name=cat.name
		category_slug=cat.slug
	if cat_id == "":
		abort(404)
	posts=Post.query.filter_by(category_id=cat_id).order_by(Post.id.desc()).limit(limit).offset(int(int(int(pagination)-1)*limit))
	pagin=math.ceil((Post.query.filter_by(category_id=cat_id).count())/limit)
	if(math.ceil(Post.query.filter_by(category_id=cat_id).count())%limit != 0 ):
		pagin=int(pagin+1)
	return render_template(template+'/category.html',page_name='category',category_slug=category_slug,category_name=category_name,posts=posts,pagin=int(pagin),current_pagin=int(pagination))
@app.route('/search/<pagination>', methods=['POST', 'GET'])
@app.route('/search/<pagination>/', methods=['POST', 'GET'])
@app.route('/sw/<pagination>', methods=['POST', 'GET'])
@app.route('/sw/<pagination>/', methods=['POST', 'GET'])
@app.route('/search', methods=['POST', 'GET'])
@app.route('/search/', methods=['POST', 'GET'])
@app.route('/sw', methods=['POST', 'GET'])
@app.route('/sw/', methods=['POST', 'GET'])
def search(pagination=1):
	global limit
	search=(str(request.args['q']))
	search=search.replace(" ",'+')
	if search=="":
		return redirect(url_for("index"))
	posts=Post.query.filter((Post.title).match("'%"+search+"%'")).all()#limit(limit).offset(int(int(int(limit)-1)*limit))
	pagin=math.ceil((Post.query.filter((Post.title).match("'%"+search+"%'")).count())/limit)
	if math.ceil(pagin)%limit != 0:
		pagin=int(pagin+1)
	return render_template(template+'/search.html',search=search,page_name='search',posts=posts,current_pagin=int(pagination),pagin=(int(pagin)))

	# search=(str(request.args['q']))#.split()
	# search=search.replace(" ",'+')
	# # return search
	# if search=="":
	# 	return redirect(url_for("index"))
	# query_result=(Post.query.filter((Post.title).match("'%"+search+"%'"))).count()
	# posts=Post.query.filter((Post.title).match("'%"+search+"%'")).all()#.limit(limit).offset(int(int(int(limit)-1)*limit))
	# return render_template(template+"/search.html",search=search,query_result=query_result,posts=posts)


# @app.route('/search', methods=['POST', 'GET'])
# @app.route('/search/', methods=['POST', 'GET'])
# def booking():
# 	return render_template(template+'/booking.html')
#end client
if __name__ == '__main__':
	 app.run(use_reloader=False,debug = True,host='0.0.0.0')
#replace white space:
#http://docs.python-requests.org/en/master/user/quickstart/