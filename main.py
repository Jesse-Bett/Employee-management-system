from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# Adding a config
LOCAL_DB_LINK= ''
HEROKU_BD=''
app.config['SQLALCHEMY_DATABASE_URI'] = LOCAL_DB_LINK
app.config['SECRET_KEY'] = os.urandom(20)

db = SQLAlchemy(app)

# importing models
from models.payroll_model import Payroll
from models.payroll_class import Payroll_C
from models.employee_model import Employee
from models.department_model import Department

# creating tables for the database
@app.before_first_request
def create():
    db.create_all()

@app.route('/login',methods=['GET','POST'])
def login():

     return render_template('login.html')


@app.route('/register',methods=['GET','POST'])
def register():

     return render_template('register.html')

@app.route('/')
def home_page():

    return render_template('homepage.html')

@app.route("/employees", methods=['GET', 'POST'])
def employees():

     # fetching all departments available inthe department tables
    all_deps = Department.query.all()

    all_employees = Employee.query.all()
    if request.method == 'POST':
        name = request.form['full_names']
        email = request.form['email']
        gender = request.form['gender']
        phone_number=request.form['phone_number']
        national_id_number = request.form['national_id_no']
        age = request.form['age']
        kra_pin = request.form['kra_pin']
        dep_id = request.form['dep_id']
        salary = request.form['entered_salary']
        benefits = request.form['entered_benefits']
        

        # sending info to the db
        # create an object of the Employee class
        print(name)
        if Employee.checking_employee(national_id_number):

            flash('Employee exists.Similar nationall id number exists','warning')
            # returns you to ur previous stage.it takes the function name of the route
            return redirect(url_for('employees'))

            # calling function to check if kra exists.
        elif Employee.check_kra_exists(kra_pin):
            flash(' Cannot create employee! KRA PIN exists in this system','warning')
            return redirect(url_for('employees'))
        else:
            # this equates the  the columns where data will be inputed and values to be inputed
            emp = Employee(employee_name=name, employee_email=email,
                           employee_gender=gender, employee_national_id=national_id_number, employee_age=age, employee_KRA_PIN=kra_pin, department_id=dep_id,employee_salary=salary,employee_benefits=benefits,employee_phone_number=phone_number)
            # this calls the function fro the employee_models to commit te data to the db

            emp.create()
            flash('Successfully created','info')
            return redirect(url_for('employees'))
    return render_template('employees.html', depart=all_deps, all_emps=all_employees)


@app.route('/departments', methods=['GET', 'POST'])
def departments():

    # fetchting all departments
    all_dep = Department.fetch_all()
    if request.method == 'POST':
        department = request.form['department_name_entered']
        
        if Department.checker_department(department):
            flash('Department alredy exists','warning')
            return redirect(url_for('departments'))
        else:
            dep = Department(department_name=department)
            dep.create()
            flash('Success! Department created','info')
            return redirect(url_for('departments'))

    return render_template('departments.html', all_depart=all_dep)


# CREATING A ROUTE FOR EDITING THE DEPARTMENT
@app.route('/departments/edit/<int:id>', methods=['POST', 'GET'])
def update_department(id):
    if request.method == 'POST':
        name = request.form['updated_department']
 
        update_depart = Department.update_by_id(id=id, department=name)

        if update_depart:
            print('updated')
            flash('Update succesfull','info')

        return redirect(url_for('departments'))

# CREATING A ROUTE TO EDIT EMPLOYEE DETAILS
@app.route('/employees/edit/<int:id>', methods=['POST', 'GET'])
def update_employee(id):
    if request.method=='POST':
        full_names= request.form['full_names']
        email=request.form['email']
        national_id_no=request.form['national_id_no']
        phone_number=request.form['phone_number']
        gender=request.form['gender']
        age=request.form['age']
        kra_pin=request.form['kra_pin']
        update_salary=request.form['update_salary']
        update_benefits=request.form['update_benefits']
        dep_id=request.form['dep_id']

        try:
    
            updates = Employee.update_details(id=id,employee_name=full_names,email=email,kra=kra_pin,salary=update_salary,benefits=update_benefits,age=age,gender=gender,national_id=national_id_no,phone_number=phone_number,update_department_id=dep_id)
            flash(f'updates on employee named {full_names} done succesfully','info')
            return redirect(url_for('employees'))
        except Exception:
            flash('un error occured .plz retry','danger')
            return redirect(url_for('employees'))


# creating a deleting route
@app.route('/employees/delete/<int:id>', methods=['POST', 'GET'])
def delete_employee(id):
    # calling function to delete the employee
    emp= Employee.fetching_all_emps_by_id_test(id=id)
    # print(emp.employee_name)
    try:
        deleted_employee_of_id = Employee.delete_employee(id)
        flash('Employee DELETED')
    except Exception:
        flash(f' cannot delete employee named  {emp.employee_name} because he/she has payrolls. Consider clearing the payroll first','warning')

    return redirect(url_for('employees'))

# creating a route to delete department
@app.route('/departments/delete/<int:id>', methods=['POST', 'GET'])
def delete_department_by_id(id):

    # calling method to delete from the departments model
    try:
        recieved_delete_content = Department.deleting_department_by_id(id)
    except Exception:
        flash('cannot delete department because it has employees','warning')

    return redirect(url_for('departments'))


# creating route to view  employees in a department
@app.route('/department/employees/<int:id>', methods=['POST', 'GET'])
def geting_employees_in_deps(id):

    deprt = Department.fetching_department_by_id(id)
        # fetchting all employees in the db
    all_employees = Employee.query.all()

    emp = deprt.employee
    return render_template('view_emps_in_dps.html', sekta=deprt,all_employees=all_employees,emp=emp)
# succes payroll.route

@app.route('/payroll/success<int:id>',methods=['GET','POST'])
def success_payroll(id):
    if request.method=='POST':
        monthy =request.form['month']
            # fetching all emps with.. the id in this roue is gotten from payroll route in  the loop in th payroll.html
        print(id)
        success_all_emps= Employee.query.filter_by(id=id)
        for anything in success_all_emps:
            # print(anything.payroll_.gross_salary)
            employee_id=anything.id
            salary=anything.employee_salary
            benefits=anything.employee_benefits
            
        # instantiating gen_subs_payroll to payroll_()
        gen_subs_payroll = Payroll_C(basic_salary=salary,benefits=benefits)

        gross_salary=gen_subs_payroll.calculate_gross_salary()
        taxable_income = gen_subs_payroll.calculate_taxable_income()
        nssf_contribution = gen_subs_payroll.calculate_nssf()
        nhif_contribution = gen_subs_payroll.calculate_nhif()
        payee = gen_subs_payroll.calculate_payee()
        total_tax_payable= gen_subs_payroll.calculate_tax_payable()
        net_salary = gen_subs_payroll.calculate_net_salary()
  
                # connectin to db
        db_payroll= Payroll(basic_salary=salary,benefits=benefits,gross_salary=gross_salary,
        taxable_income=taxable_income,nssf_contribution=nssf_contribution,nhif_contribution=nhif_contribution,
        payee=payee,total_tax_payable=total_tax_payable,net_salary=net_salary,month=monthy,employee_id=employee_id)

        # fetch_payroll=Payroll.fetch_payroll_employee_id(id)
        fetch_payroll=Payroll.query.filter_by(employee_id=id).first()
        
        db_payroll.create()
        flash(f'payroll for {anything.employee_name} for moonth {monthy} has been generated. ','success')
        return redirect(url_for('payroll',id=id))
        # return render_template('generated_payroll.html',fetch_payroll=fetch_payroll)

    return render_template('generated_payroll.html')

# view previous payrolls
@app.route('/view_payrolls/<int:id>')
def view_payrolls(id):
       
    
    # fetching payrolls with foriengkey employee id
    fetched_payroll=Payroll.fetch_payroll_employee_id(employee_id=id)
    global id_of_employee_on_payroll
    id_of_employee_on_payroll=id

    return render_template('view_payroll.html',fetched_payroll=fetched_payroll)


@app.route('/payroll/<int:id>')
def payroll(id):

    all_emps = Employee.query.filter_by(id=id)
    return render_template('payroll.html',all_emps=all_emps)

# route to delete payroll
@app.route('/payroll/delete/<int:id>',methods=['POST','GET'])
def delete_payroll(id):

    try:
        delete_payroll_id = Payroll.deleting_payroll(id=id)
        print(delete_payroll_id)
        flash('payroll deleted','success')
        print('deleted')
    except Exception:
        flash('an error occured! retry...')

    return redirect(url_for('view_payrolls', id=id_of_employee_on_payroll ))

    

if __name__ == '__main__':
    app.run(debug=True)
