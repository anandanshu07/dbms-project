from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mukeshgutka' # Change this to a strong, random key

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root', # e.g., 'root'
    'password': 'hard7011',
    'database': 'hospital_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

# --- Department Routes ---
@app.route('/departments')
def departments():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM DEPARTMENT ORDER BY Department_Name")
    departments_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('departments.html', departments=departments_data)

@app.route('/departments/add', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        dept_name = request.form['department_name']
        location = request.form['location']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'error')
            return redirect(url_for('departments'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO DEPARTMENT (Department_Name, Location) VALUES (%s, %s)", (dept_name, location))
            conn.commit()
            flash('Department added successfully!', 'success')
            return redirect(url_for('departments'))
        except mysql.connector.Error as err:
            flash(f"Error adding department: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    return render_template('add_department.html')

@app.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('departments'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        dept_name = request.form['department_name']
        location = request.form['location']
        try:
            cursor.execute("UPDATE DEPARTMENT SET Department_Name = %s, Location = %s WHERE Department_ID = %s", (dept_name, location, id))
            conn.commit()
            flash('Department updated successfully!', 'success')
            return redirect(url_for('departments'))
        except mysql.connector.Error as err:
            flash(f"Error updating department: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM DEPARTMENT WHERE Department_ID = %s", (id,))
        department = cursor.fetchone()
        cursor.close()
        conn.close()
        if department:
            return render_template('edit_department.html', department=department)
        else:
            flash('Department not found.', 'error')
            return redirect(url_for('departments'))

@app.route('/departments/delete/<int:id>', methods=['POST'])
def delete_department(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('departments'))
    cursor = conn.cursor()
    try:
        # Check for related doctors before deleting
        cursor.execute("SELECT COUNT(*) FROM DOCTOR WHERE Department_ID = %s", (id,))
        doctor_count = cursor.fetchone()[0]
        if doctor_count > 0:
            flash('Cannot delete department with associated doctors. Please reassign doctors first.', 'error')
        else:
            cursor.execute("DELETE FROM DEPARTMENT WHERE Department_ID = %s", (id,))
            conn.commit()
            flash('Department deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error deleting department: {err}", 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('departments'))


# --- Doctor Routes ---
@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT D.*, DEP.Department_Name
        FROM DOCTOR D
        JOIN DEPARTMENT DEP ON D.Department_ID = DEP.Department_ID
        ORDER BY D.Doctor_Name
    """)
    doctors_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctors.html', doctors=doctors_data)

@app.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('doctors'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Department_ID, Department_Name FROM DEPARTMENT ORDER BY Department_Name")
    departments = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        specialization = request.form['specialization']
        phone_number = request.form['phone_number']
        department_id = request.form['department_id']
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO DOCTOR (Doctor_Name, Specialization, PhoneNumber, Department_ID) VALUES (%s, %s, %s, %s)",
                           (doctor_name, specialization, phone_number, department_id))
            conn.commit()
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('doctors'))
        except mysql.connector.Error as err:
            flash(f"Error adding doctor: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        conn.close()
    return render_template('add_doctor.html', departments=departments)


@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('doctors'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        specialization = request.form['specialization']
        phone_number = request.form['phone_number']
        department_id = request.form['department_id']
        try:
            cursor.execute("UPDATE DOCTOR SET Doctor_Name = %s, Specialization = %s, PhoneNumber = %s, Department_ID = %s WHERE Doctor_ID = %s",
                           (doctor_name, specialization, phone_number, department_id, id))
            conn.commit()
            flash('Doctor updated successfully!', 'success')
            return redirect(url_for('doctors'))
        except mysql.connector.Error as err:
            flash(f"Error updating doctor: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM DOCTOR WHERE Doctor_ID = %s", (id,))
        doctor = cursor.fetchone()
        cursor.execute("SELECT Department_ID, Department_Name FROM DEPARTMENT ORDER BY Department_Name")
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        if doctor:
            return render_template('edit_doctor.html', doctor=doctor, departments=departments)
        else:
            flash('Doctor not found.', 'error')
            return redirect(url_for('doctors'))

@app.route('/doctors/delete/<int:id>', methods=['POST'])
def delete_doctor(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('doctors'))
    cursor = conn.cursor()
    try:
        # Check for related appointments or medical records before deleting
        cursor.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE Doctor_ID = %s", (id,))
        appointment_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MEDICAL_RECORD WHERE Doctor_ID = %s", (id,))
        record_count = cursor.fetchone()[0]

        if appointment_count > 0 or record_count > 0:
            flash('Cannot delete doctor with associated appointments or medical records.', 'error')
        else:
            cursor.execute("DELETE FROM DOCTOR WHERE Doctor_ID = %s", (id,))
            conn.commit()
            flash('Doctor deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error deleting doctor: {err}", 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('doctors'))


# --- Patient Routes ---
@app.route('/patients')
def patients():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PATIENT ORDER BY Patient_Name")
    patients_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patients.html', patients=patients_data)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        address = request.form['address']
        dob = request.form['dob'] # YYYY-MM-DD
        gender = request.form['gender']
        phone_number = request.form['phone_number']

        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed.', 'error')
            return redirect(url_for('patients'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO PATIENT (Patient_Name, Address, DOB, Gender, PhoneNumber) VALUES (%s, %s, %s, %s, %s)",
                           (patient_name, address, dob, gender, phone_number))
            conn.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients'))
        except mysql.connector.Error as err:
            flash(f"Error adding patient: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    return render_template('add_patient.html')

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('patients'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        address = request.form['address']
        dob = request.form['dob']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        try:
            cursor.execute("UPDATE PATIENT SET Patient_Name = %s, Address = %s, DOB = %s, Gender = %s, PhoneNumber = %s WHERE Patient_ID = %s",
                           (patient_name, address, dob, gender, phone_number, id))
            conn.commit()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('patients'))
        except mysql.connector.Error as err:
            flash(f"Error updating patient: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM PATIENT WHERE Patient_ID = %s", (id,))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        if patient:
            # Format DOB for HTML input type="date"
            if patient['DOB']:
                patient['DOB_formatted'] = patient['DOB'].strftime('%Y-%m-%d')
            return render_template('edit_patient.html', patient=patient)
        else:
            flash('Patient not found.', 'error')
            return redirect(url_for('patients'))

@app.route('/patients/delete/<int:id>', methods=['POST'])
def delete_patient(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('patients'))
    cursor = conn.cursor()
    try:
        # Check for related appointments or medical records before deleting
        cursor.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE Patient_ID = %s", (id,))
        appointment_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MEDICAL_RECORD WHERE Patient_ID = %s", (id,))
        record_count = cursor.fetchone()[0]

        if appointment_count > 0 or record_count > 0:
            flash('Cannot delete patient with associated appointments or medical records.', 'error')
        else:
            cursor.execute("DELETE FROM PATIENT WHERE Patient_ID = %s", (id,))
            conn.commit()
            flash('Patient deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error deleting patient: {err}", 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('patients'))


# --- Appointment Routes ---
@app.route('/appointments')
def appointments():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT A.*, P.Patient_Name, D.Doctor_Name
        FROM APPOINTMENT A
        JOIN PATIENT P ON A.Patient_ID = P.Patient_ID
        JOIN DOCTOR D ON A.Doctor_ID = D.Doctor_ID
        ORDER BY A.Appointment_Date DESC
    """)
    appointments_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('appointments.html', appointments=appointments_data)

@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('appointments'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Patient_ID, Patient_Name FROM PATIENT ORDER BY Patient_Name")
    patients = cursor.fetchall()
    cursor.execute("SELECT Doctor_ID, Doctor_Name, Specialization FROM DOCTOR ORDER BY Doctor_Name")
    doctors = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        appointment_date_str = request.form['appointment_date']
        status = request.form['status']
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']

        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date/time format. Please use YYYY-MM-DDTHH:MM.', 'error')
            conn.close()
            return render_template('add_appointment.html', patients=patients, doctors=doctors)

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO APPOINTMENT (Appointment_Date, Status, Patient_ID, Doctor_ID) VALUES (%s, %s, %s, %s)",
                           (appointment_date, status, patient_id, doctor_id))
            conn.commit()
            flash('Appointment added successfully!', 'success')
            return redirect(url_for('appointments'))
        except mysql.connector.Error as err:
            flash(f"Error adding appointment: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        conn.close()
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

@app.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('appointments'))
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT Patient_ID, Patient_Name FROM PATIENT ORDER BY Patient_Name")
    patients = cursor.fetchall()
    cursor.execute("SELECT Doctor_ID, Doctor_Name, Specialization FROM DOCTOR ORDER BY Doctor_Name")
    doctors = cursor.fetchall()

    if request.method == 'POST':
        appointment_date_str = request.form['appointment_date']
        status = request.form['status']
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']

        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date/time format. Please use YYYY-MM-DDTHH:MM.', 'error')
            conn.close()
            return render_template('edit_appointment.html', patients=patients, doctors=doctors, appointment={'Appointment_ID': id})


        try:
            cursor.execute("UPDATE APPOINTMENT SET Appointment_Date = %s, Status = %s, Patient_ID = %s, Doctor_ID = %s WHERE Appointment_ID = %s",
                           (appointment_date, status, patient_id, doctor_id, id))
            conn.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointments'))
        except mysql.connector.Error as err:
            flash(f"Error updating appointment: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM APPOINTMENT WHERE Appointment_ID = %s", (id,))
        appointment = cursor.fetchone()
        cursor.close()
        conn.close()
        if appointment:
            if appointment['Appointment_Date']:
                # Format for HTML input type="datetime-local"
                appointment['Appointment_Date_formatted'] = appointment['Appointment_Date'].strftime('%Y-%m-%dT%H:%M')
            return render_template('edit_appointment.html', appointment=appointment, patients=patients, doctors=doctors)
        else:
            flash('Appointment not found.', 'error')
            return redirect(url_for('appointments'))

@app.route('/appointments/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('appointments'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM APPOINTMENT WHERE Appointment_ID = %s", (id,))
        conn.commit()
        flash('Appointment deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error deleting appointment: {err}", 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('appointments'))


# --- Medical Record Routes ---
@app.route('/medical_records')
def medical_records():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('index'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT MR.*, P.Patient_Name, D.Doctor_Name
        FROM MEDICAL_RECORD MR
        JOIN PATIENT P ON MR.Patient_ID = P.Patient_ID
        JOIN DOCTOR D ON MR.Doctor_ID = D.Doctor_ID
        ORDER BY MR.Record_ID DESC
    """)
    medical_records_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('medical_records.html', medical_records=medical_records_data)

@app.route('/medical_records/add', methods=['GET', 'POST'])
def add_medical_record():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('medical_records'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Patient_ID, Patient_Name FROM PATIENT ORDER BY Patient_Name")
    patients = cursor.fetchall()
    cursor.execute("SELECT Doctor_ID, Doctor_Name, Specialization FROM DOCTOR ORDER BY Doctor_Name")
    doctors = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        symptoms = request.form['symptoms']
        diagnosis = request.form['diagnosis']
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO MEDICAL_RECORD (Symptoms, Diagnosis, Patient_ID, Doctor_ID) VALUES (%s, %s, %s, %s)",
                           (symptoms, diagnosis, patient_id, doctor_id))
            conn.commit()
            flash('Medical record added successfully!', 'success')
            return redirect(url_for('medical_records'))
        except mysql.connector.Error as err:
            flash(f"Error adding medical record: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        conn.close()
    return render_template('add_medical_record.html', patients=patients, doctors=doctors)

@app.route('/medical_records/edit/<int:id>', methods=['GET', 'POST'])
def edit_medical_record(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('medical_records'))
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT Patient_ID, Patient_Name FROM PATIENT ORDER BY Patient_Name")
    patients = cursor.fetchall()
    cursor.execute("SELECT Doctor_ID, Doctor_Name, Specialization FROM DOCTOR ORDER BY Doctor_Name")
    doctors = cursor.fetchall()

    if request.method == 'POST':
        symptoms = request.form['symptoms']
        diagnosis = request.form['diagnosis']
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        try:
            cursor.execute("UPDATE MEDICAL_RECORD SET Symptoms = %s, Diagnosis = %s, Patient_ID = %s, Doctor_ID = %s WHERE Record_ID = %s",
                           (symptoms, diagnosis, patient_id, doctor_id, id))
            conn.commit()
            flash('Medical record updated successfully!', 'success')
            return redirect(url_for('medical_records'))
        except mysql.connector.Error as err:
            flash(f"Error updating medical record: {err}", 'error')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM MEDICAL_RECORD WHERE Record_ID = %s", (id,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        if record:
            return render_template('edit_medical_record.html', record=record, patients=patients, doctors=doctors)
        else:
            flash('Medical record not found.', 'error')
            return redirect(url_for('medical_records'))

@app.route('/medical_records/delete/<int:id>', methods=['POST'])
def delete_medical_record(id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed.', 'error')
        return redirect(url_for('medical_records'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM MEDICAL_RECORD WHERE Record_ID = %s", (id,))
        conn.commit()
        flash('Medical record deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error deleting medical record: {err}", 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('medical_records'))


if __name__ == '__main__':
    app.run(debug=True)