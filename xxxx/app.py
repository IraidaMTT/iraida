from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
#import pdfkit
import jinja2
from tkinter import filedialog as FileDialog
from tkinter.messagebox import askokcancel, showinfo, WARNING

app = Flask(__name__)
app.secret_key = "MySecretKey"
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bdlineas'

mysql.init_app(app)


@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/ReporteG')
def ReporteG():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    msql = "SELECT lineas.PlanVoz, Count(lineas.Numero) AS CuentaDeNumero, Sum(ifnull(lineas.TarifaVoz,0)) AS Importe FROM lineas GROUP BY lineas.PlanVoz ORDER BY lineas.PlanVoz DESC;"
    cursor.execute(msql)
    datosV = cursor.fetchall()
    cursor.close

    cursor = conexion.cursor()
    msql = "SELECT lineas.PlanMSG, Count(lineas.Numero) AS CuentaDeNumero, Sum(round(ifnull(lineas.TarifaMSG,0),2)) AS Importe FROM lineas GROUP BY lineas.PlanMSG ORDER BY lineas.PlanMSG DESC;"
    cursor.execute(msql)
    datosM = cursor.fetchall()
    cursor.close

    cursor = conexion.cursor()
    msql = "SELECT ifnull(lineas.PlanDatos,''), Count(lineas.Numero) AS CuentaDeNumero, Sum(ifnull(lineas.TarifaDatos,0)) AS Importe FROM lineas GROUP BY ifnull(lineas.PlanDatos,'') ORDER BY lineas.PlanDatos DESC;"
    cursor.execute(msql)
    datosD = cursor.fetchall()
    cursor.close

    cursor = conexion.cursor()
    msql = "SELECT Count(lineas.Numero) AS CuentaDeNumero, Sum(round(lineas.TarifaVoz,2)) AS importeVoz, Sum(round(lineas.TarifaMSG,2)) AS importeMSG, Sum(round(lineas.TarifaDatos,2)) AS importeDatos, lineas.Historia FROM lineas GROUP BY lineas.Historia HAVING (((lineas.Historia)=False));"
    cursor.execute(msql)
    TotalL = cursor.fetchall()
    cursor.close

    info=(TotalL,datosV,datosM,datosD)

    return render_template('sitio/ReporteG.html', info=info)


@app.route('/busqueda', methods=['POST'])
def burcar():
    _item = request.form['BItem']
    
    print(__name__ )
    
    if len(_item)==0 :
        return render_template('sitio/index.html')
    else:
        conexion = mysql.connect()
        cursor = conexion.cursor()
        msql = "SELECT areas.Area, asignacion.numero, (lineas.TarifaVoz + lineas.TarifaMSG + lineas.TarifaDatos) AS Precio, trabajadores.nombre FROM lineas RIGHT JOIN (asignacion RIGHT JOIN (areas LEFT JOIN trabajadores ON areas.IDArea = trabajadores.IDArea) ON asignacion.CI = trabajadores.CI) ON lineas.Numero = asignacion.numero WHERE ((InStr(asignacion.numero, %s)<>0) or (InStr(trabajadores.nombre, %s)<>0)) ORDER BY lineas.numero DESC;"
        datos= (_item, _item)
        cursor.execute(msql, datos)
        mdatos = cursor.fetchall()
        cursor.close
        return render_template('sitio/informe.html', xx = mdatos, item=_item)


@app.route('/Abusqueda', methods=['POST'])
def Aburcar():
    _item = request.form['BItem']
    
    print(__name__ )
    
    if len(_item)==0 :
        return render_template('admin/index.html')
    else:
        conexion = mysql.connect()
        cursor = conexion.cursor()
        msql = "SELECT areas.Area, trabajadores.nombre, asignacion.numero, lineas.PIN, lineas.PUK, lineas.usuario, lineas.contrasena, (lineas.TarifaVoz + lineas.TarifaMSG + lineas.TarifaDatos) AS Precio FROM lineas RIGHT JOIN (asignacion RIGHT JOIN (areas LEFT JOIN trabajadores ON areas.IDArea = trabajadores.IDArea) ON asignacion.CI = trabajadores.CI) ON lineas.Numero = asignacion.numero WHERE ((InStr(asignacion.numero, %s)<>0) or (InStr(trabajadores.nombre, %s)<>0)) ORDER BY lineas.numero DESC;"
        datos= (_item, _item)
        cursor.execute(msql, datos)
        mdatos = cursor.fetchall()
        cursor.close
        return render_template('admin/Ainforme.html', xx = mdatos, item=_item)


@app.route('/lineas')
def MostrarLineas():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    msql = "SELECT ifnull(areas.Area,''), lineas.numero, (ifnull(TarifaVoz,0)+ifnull(TarifaMSG,0)+ifnull(TarifaDatos,0)) AS Precio, ifnull(trabajadores.nombre,'') AS nombre, ifnull(lineas.PlanVoz,''), ifnull(lineas.PlanMSG,''), ifnull(lineas.PlanDatos,'') FROM areas RIGHT JOIN (trabajadores RIGHT JOIN (lineas LEFT JOIN asignacion ON lineas.Numero = asignacion.numero) ON trabajadores.CI = asignacion.CI) ON areas.IDArea = lineas.IDArea WHERE (((lineas.Historia)=False)) GROUP BY areas.Area, lineas.numero ORDER BY Precio DESC, nombre;"
    cursor.execute(msql)
    mdatos = cursor.fetchall()
    cursor.close
    cursor = conexion.cursor()
    msql = "SELECT areas.IdArea, areas.Area, COUNT(lineas.numero) AS Tlineas,  sum(round((ifnull(lineas.TarifaVoz, 0) + ifnull(lineas.TarifaMSG, 0) + ifnull(lineas.TarifaDatos,0)),2))  AS TPrecio FROM lineas RIGHT JOIN areas ON areas.IDArea = lineas.IDArea GROUP BY areas.Area ORDER BY areas.IdArea;"
    cursor.execute(msql)
    mareas = cursor.fetchall()
    cursor.close
    msql = "SELECT COUNT(lineas.numero) AS Tlineas, sum(round((ifnull(lineas.TarifaVoz, 0) + ifnull(lineas.TarifaMSG, 0) + ifnull(lineas.TarifaDatos,0)),2)) AS TPrecio FROM lineas;"
    cursor.execute(msql)
    tdatos = cursor.fetchall()
    cursor.close
    conexion.close
    return render_template('sitio/lineasxareas.html', mdatos=mdatos, mareas=mareas, tdatos=tdatos)


@app.route('/t_areas')
def MostrarTLineas():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    msql = "SELECT COUNT(lineas.numero) AS Tlineas, sum((round(lineas.TarifaVoz + lineas.TarifaMSG + lineas.TarifaDatos,2))) AS TPrecio FROM lineas;"
    cursor.execute(msql)

    tdatos = cursor.fetchall()
    cursor.close
    cursor = conexion.cursor()
    msql = "SELECT areas.IdArea, areas.Area, COUNT(lineas.numero) AS Tlineas,  sum((round(lineas.TarifaVoz + lineas.TarifaMSG + lineas.TarifaDatos,2))) AS TPrecio FROM lineas RIGHT JOIN areas ON areas.IDArea = lineas.IDArea GROUP BY areas.Area ORDER BY areas.IdArea;"
    cursor.execute(msql)

    mareas = cursor.fetchall()
    cursor.close
    conexion.close
    return render_template('sitio/t_areas.html', tdatos=tdatos, mareas=mareas)


@app.route('/admin')
def Administrar():
    if not 'login' in session:
        return render_template('admin/login.html')
    return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['TxtUsuario']
    _contrasena = request.form['TxtSena']

    if _usuario == "admin" and _contrasena == "Cimab2023*":
        session["login"] = True
        session["usuario"] = "Administrador"
        return redirect('/admin')
    else:
        print("Nombre de usuario o contraseña incorrecta..")

    return render_template('admin/login.html')


@app.route('/admin/login/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/')

@ app.route('/admin/areas')
def MAreas():
    if not 'login' in session:
        return render_template('admin/login.html')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT IDArea, Area, Siglas FROM areas")
    areas = cursor.fetchall()
    conexion.commit()
    return render_template('admin/areas.html', areas=areas)


@ app.route('/admin/areas/guardar', methods=['POST'])
def admin_areas_guardar():
    _miidarea = request.form['MIDArea']
    _miarea = request.form['MArea']
    _misarea = request.form['MSArea']
    sql = "INSERT INTO areas (IDArea, Area, Siglas) VALUES (%s,%s,%s);"
    datos = (_miidarea, _miarea, _misarea)
    conexion = mysql.connect() 
    cursor=conexion.cursor() 
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/areas')


@ app.route('/admin/areas/borrar/<string:_id>')
def admin_areas_borrar(_id):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM areas WHERE IDArea=%s", _id)
    conexion.commit()
    return redirect('/admin/areas')


@ app.route('/admin/areas/editar/<string:_id>')
def admin_areas_editar(_id):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT IDArea, Area, Siglas FROM areas WHERE IDArea=%s",_id)
    areas = cursor.fetchall()                                   
    conexion.commit()
    cursor.close
    return render_template('admin/Edita_areas.html', area=areas[0])

@ app.route('/admin/areas/salvar/<_id>', methods=['POST'])
def Salvar(_id):
    _miarea = request.form['MArea']
    _misarea = request.form['MSArea']
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("UPDATE areas SET Area=%s, Siglas=%s WHERE IDArea=%s",(_miarea,_misarea,_id))
    conexion.commit()
    cursor.close
    return redirect('/admin/areas')


@app.route('/admin/trabajadores')
def MTrabajadores():
    if not 'login' in session:
        return render_template('admin/login.html')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT trabajadores.CI, trabajadores.Nombre, areas.Area, trabajadores.Historia, areas.IDArea FROM areas RIGHT JOIN trabajadores ON areas.IDArea = trabajadores.IDArea ORDER BY trabajadores.IDArea;")
    trabajadores = cursor.fetchall()

    cursor.execute("SELECT * FROM areas;")
    areas = cursor.fetchall()
    conexion.commit()
    return render_template('admin/trabajadores.html', trabajadores=trabajadores, areas=areas)


@app.route('/admin/trabajadores/guardar', methods=['POST'])
def admin_trabajadores_guardar():
    _mici = request.form['MCI']
    _minombre = request.form['MNombre']
    _miarea = request.form['MArea']
    sql = "INSERT INTO trabajadores (CI, Nombre, IDArea, historia) VALUES (%s,%s,%s,0);"
    datos = (_mici, _minombre, _miarea)
    print(datos)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/trabajadores')


@app.route('/admin/trabajadores/borrar/<string:_id>')
def admin_trabajadores_borrar(_id):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM trabajadores WHERE CI=%s", (_id))
    conexion.commit()
    return redirect('/admin/trabajadores')

@ app.route('/admin/trabajadores/editar/<string:_id>')
def admin_trab_editar(_id):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT trabajadores.CI, trabajadores.Nombre, areas.Area, trabajadores.Historia, trabajadores.IDArea FROM areas RIGHT JOIN trabajadores ON areas.IDArea = trabajadores.IDArea WHERE CI=%s",_id)
    trabajadores = cursor.fetchall()                                   
    conexion.commit()
    cursor.close
    cursor.execute("SELECT * FROM areas;")
    areas = cursor.fetchall()
    conexion.commit()
    return render_template('admin/Edita_trabajadores.html', trabajador=trabajadores[0], areas=areas)



@ app.route('/admin/trabajadores/salvar/<_id>', methods=['POST'])
def SalvarT(_id):
    _minombre = request.form['MNombre']
    _miarea = request.form['MArea']
    _mihist= request.form['MHistoria']
    print(_minombre,_miarea,_mihist,_id)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("UPDATE trabajadores SET Nombre=%s, IDArea=%s, Historia=%s WHERE CI=%s",(_minombre,_miarea,_mihist,_id))
    conexion.commit()
    cursor.close
    return redirect('/admin/trabajadores') 



@ app.route('/admin/lineas')
def Mlineas():
    if not 'login' in session:
        return render_template('admin/login.html')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT lineas.Numero, areas.Siglas, DATE_FORMAT(lineas.FechaCompra,'%m/%y') AS fecha, lineas.PlanVoz, lineas.TarifaVoz, lineas.PlanMSG, lineas.TarifaMSG, lineas.PlanDatos, lineas.TarifaDatos, lineas.PIN, lineas.PUK, lineas.usuario, lineas.contrasena, lineas.IP, lineas.MAC, lineas.historia, lineas.Observaciones FROM areas RIGHT JOIN lineas ON areas.IDArea = lineas.IDArea;")
    lineas = cursor.fetchall()
    conexion.commit()
    cursor.close
    cursor.execute("SELECT * FROM areas;")
    areas = cursor.fetchall()
    conexion.commit()
    rutaF='D:\\SitioLineas\\templates\\admin\\ImpLineas.html'
   # CreaMiPDF(rutaF,info=lineas,rutacss='')

    return render_template('admin/lineas.html', lineas=lineas, areas=areas)


@ app.route('/admin/lineas/guardar', methods=['POST'])
def admin_lineas_guardar():
    _mnum = request.form['Mnumero']
    _mida = request.form['MArea']
    _mfech = request.form['Mfecha']
    _mvoz = request.form['Mvoz']
    _mnsg = request.form['MMsg']
    _mdatos = request.form['Mdatos']
    _mpreciod = request.form['MprecioD']
    _mpreciov = request.form['MprecioV']
    _mpreciom = request.form['MprecioM']
    _mpin = request.form['Mpin']
    _mpuk = request.form['Mpuk']
    _musuar = request.form['Musuar']
    _msena = request.form['Msena']
    _mip = request.form['Mip']
    _mmac = request.form['Mmac']
    _mobs = request.form['MObsr']
    sql = "INSERT INTO lineas(Numero, IDArea, FechaCompra, PlanVoz, PlanMSG, PlanDatos, TarifaDatos, TarifaVoz, TarifaMSG, PIN, PUK, usuario, contrasena, IP, MAC, Observaciones,historia) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0);"
    datos = (_mnum,_mida, _mfech, _mvoz, _mnsg, _mdatos, _mpreciod, _mpreciov, _mpreciom, _mpin, _mpuk, _musuar, _msena, _mip, _mmac, _mobs)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/lineas')


@ app.route('/admin/lineas/borrar/<_id>')
def admin_lineas_borrar(_id):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM lineas WHERE numero=%s", _id)
    conexion.commit()
    return redirect('/admin/lineas')

@ app.route('/admin/lineas/editar/<_idL>')
def admin_lineas_editar(_idL):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT lineas.Numero, areas.Area, lineas.FechaCompra, lineas.PlanVoz, lineas.TarifaVoz, lineas.PlanMSG, lineas.TarifaMSG, lineas.PlanDatos, lineas.TarifaDatos, lineas.PIN, lineas.PUK, lineas.usuario, lineas.contrasena, lineas.IP, lineas.MAC, lineas.historia, lineas.Observaciones, lineas.IDArea FROM areas RIGHT JOIN lineas ON areas.IDArea = lineas.IDArea WHERE lineas.numero=%s;",_idL)
    lineas = cursor.fetchall()                                   
    conexion.commit()
    cursor.close
    cursor.execute("SELECT * FROM areas;")
    areas = cursor.fetchall()
    conexion.commit()
    return render_template('admin/Edita_lineas.html', linea=lineas[0], areas=areas)



@ app.route('/admin/lineas/salvar/<_idL>', methods=['POST'])
def SalvarL(_idL):
    _mnum = request.form['Mnumero']
    _mida = request.form['MArea']
    _mfech = request.form['Mfecha']
    _mvoz = request.form['Mvoz']
    _mnsg = request.form['MMsg']
    _mdatos = request.form['Mdatos']
    _mpreciod = request.form['MprecioD']
    _mpreciov = request.form['MprecioV']
    _mpreciom = request.form['MprecioM']
    _mpin = request.form['Mpin']
    _mpuk = request.form['Mpuk']
    _musuar = request.form['Musuar']
    _msena = request.form['Msena']
    _mip = request.form['Mip']
    _mmac = request.form['Mmac']
    _mhist = request.form['Mhist']
    _mobs = request.form['MObsr']
    datos = (_mnum,_mida, _mfech, _mvoz,  _mpreciov, _mnsg, _mpreciom, _mdatos, _mpreciod, _mpin, _mpuk, _musuar, _msena, _mip, _mmac, _mhist, _mobs, _idL)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("UPDATE lineas set Numero=%s, IDArea=%s, FechaCompra=%s, PlanVoz=%s, TarifaVoz=%s, PlanMSG=%s, TarifaMSG=%s, PlanDatos=%s, TarifaDatos=%s, PIN=%s, PUK=%s, usuario=%s, contrasena=%s, IP=%s, MAC=%s, historia=%s, Observaciones=%s WHERE Numero=%s;",datos)
    conexion.commit()
    cursor.close
    return redirect('/admin/lineas') 


@ app.route('/admin/asignacion')
def MAsignacion():
    if not 'login' in session:
        return render_template('admin/login.html')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT asignacion.CI, trabajadores.nombre, asignacion.numero, asignacion.fechainicio, asignacion.fechafin, asignacion.Historia FROM asignacion LEFT JOIN trabajadores ON asignacion.CI = trabajadores.CI;")
    asignas = cursor.fetchall()
    cursor.close
    cursor.execute("SELECT * FROM lineas")
    lineas = cursor.fetchall()
    cursor.close
    cursor.execute("SELECT * FROM trabajadores")
    trabajadores = cursor.fetchall()
    conexion.commit()
    return render_template('admin/asignacion.html', asignas=asignas, lineas=lineas, trabajadores=trabajadores)


@ app.route('/admin/asignacion/guardar', methods=['POST'])
def admin_asignacion_guardar():
    _mCI = request.form['MCI']
    _mLinea = request.form['MLinea']
    _mFI = request.form['MFI']
    _mFT = request.form['MFT']
    sql = "INSERT INTO asignacion (CI, Numero, FechaInicio, FechaFin, historia) VALUES (%s,%s,%s,%s,0);"
    datos = (_mCI, _mLinea, _mFI, _mFT)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/asignacion')


@ app.route('/admin/asignacion/borrar/<_idT>,<_idL>,<_mfecha>')
def admin_asignacion_borrar(_idT, _idL, _mfecha):
    datos = (_idT, _idL, _mfecha)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    sql = "DELETE FROM asignacion WHERE asignacion.CI = %s AND asignacion.Numero = %s AND asignacion.FechaInicio = %s;"
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/asignacion')

@ app.route('/admin/asignacion/editar/<_idT>,<_idL>,<_mfecha>')
def admin_asig_editar(_idT, _idL, _mfecha):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    DATOS=(_idT, _idL, _mfecha)
    cursor.execute("SELECT asignacion.CI, trabajadores.nombre, asignacion.numero, asignacion.fechainicio, asignacion.fechafin, asignacion.Historia FROM asignacion LEFT JOIN trabajadores ON asignacion.CI = trabajadores.CI WHERE (asignacion.CI = %s) and (asignacion.numero = %s) and (asignacion.fechainicio = %s);", DATOS)
    asignas = cursor.fetchall()                                   
    conexion.commit()
    cursor.close
    return render_template('admin/Edita_asignacion.html', asigna=asignas[0])



@ app.route('/admin/asignacion/salvar/<_idT>,<_idL>,<_mfecha>', methods=['POST'])
def SalvarA(_idT, _idL, _mfecha):
    _mFI = request.form['MFI']
    _mFT = request.form['MFT']
    _mihist = request.form['mihist']
    datos=(_mFI,_mFT,_mihist,_idT,_idL,_mfecha)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("UPDATE asignacion SET fechainicio=%s, fechafin=%s, Historia=%s WHERE (CI=%s and numero=%s and fechainicio=%s)",datos)
    conexion.commit()
    cursor.close
    return redirect('/admin/asignacion') 

def CreaMiPDF(rutaF,info,rutacss=''):
    
    rutaSalida = FileDialog.asksaveasfilename(
    initialdir="C:",
    filetypes=(
        ("Ficheros PDF", "*.PDF"),
        ("Todos los ficheros", "*.*")
    ),
    title="Indicar el nombre del fichero.")
    if rutaSalida == "":
        exit()
    
   
    nombreF = rutaF.split('\\')[-1]
    rutaF = rutaF.replace(nombreF,'')

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(rutaF))
    template = env.get_template(nombreF)
    html = template.render(info=info)

    opciones={  'page-size': 'Letter',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': 'UTF-8'
              }

    config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\rene\\Downloads\\prueba\\wkhtmltox\\bin\\wkhtmltopdf.exe")   
    pdfkit.from_string(html, rutaSalida, css=rutacss, options=opciones, configuration=config)


if __name__ == '__main__':
         app.run(debug=True)
