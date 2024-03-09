from flask import Flask, render_template, request, redirect, url_for
import mysql.connector 
import random

app = Flask(__name__)

# CREAR CONEXION A BASE DE DATOS
db = mysql.connector.connect(
     host = "localhost",
     user = "root",
     password = "",
     database = "bancobd" 
)


#RUTA DE INICIO
@app.route("/",methods=["GET", "POST"])
def home() : 
    mensaje = None
    if request.method=="POST":
        NumeroCuenta=request.form["NumeroCuenta"]
        cursor = db.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM cuentas WHERE NumeroCuenta = %s", (NumeroCuenta,))
        cuenta_existe = cursor.fetchone()[0]
        cursor.close()
        if cuenta_existe:
            return redirect("/transacciones")
        else:
            mensaje = "la cuenta no existe."
    return render_template("index.html",mensaje=mensaje)


#RUTA REGISTRO
@app.route("/registro",methods=["POST"])
def registro ():
   Titular=request.form["Titular"]
   TipoCuenta= request.form.get("TipoCuenta")
   Saldo=request.form["Saldo"]
   cursor= db.cursor()

   if TipoCuenta is None:
       mensaje="eror tipo de cuenta no especificado"
       return render_template("index.html",mensaje=mensaje)
   
   NumeroCuenta=GenerarNumeroCuenta(cursor)
   cursor.execute("INSERT INTO cuentas(NumeroCuenta,TipoCuenta,Saldo,Titular) VALUES (%s,%s,%s,%s) ",
                  (NumeroCuenta,TipoCuenta,Saldo,Titular))
   
   db.commit()
   cursor.close()
   mensaje= "Cuenta creada exitosamente"
   return redirect(url_for("transacciones", CuentaOrigen=NumeroCuenta))

#NUMEROS DE CUENTA
def GenerarNumeroCuenta(cursor):
   while True:
       NumeroCuenta = ''.join(random.choices("0123456789", k=10 ))
       cursor.execute (
            "SELECT COUNT(*) FROM cuentas WHERE NumeroCuenta = %s", (NumeroCuenta,))
       cuenta_existe = cursor.fetchone()[0]
       if cuenta_existe == 0:
           break
   return NumeroCuenta

@app.route("/transacciones",methods=["GET" , "POST"])
def transacciones():
    if request.method == "POST":
        cuenta_destino=request.form["cuenta_destino"]
        CuentaOrigen=request.form["CuentaOrigen"]
        Valor=float(request.form ["Valor"])
        tipotransaccion=request.form.get("tipotransaccion")
        cursor= db.cursor()

        if tipotransaccion is None:
            mensaje= "Error no hay tipo de transaccion"
            return render_template("transacciones.html", mensaje=mensaje)
        
        cursor.execute(
            "SELECT Saldo FROM cuentas WHERE NumeroCuenta = %s", (CuentaOrigen,))
        saldo_origen = cursor.fetchone()

        if saldo_origen is None:
            mensaje="Error saldo origen no exite"
            cursor.close()
            return render_template("transacciones.html", mensaje=mensaje)
        else:
            saldo_origen=saldo_origen[0]

        if saldo_origen >= Valor: 
            cursor.execute(
                "SELECT ID FROM tipotransaccion WHERE Descripcion = %s",(tipotransaccion,))
            IDTipoTransaccion = cursor.fetchone()

            if IDTipoTransaccion is None:
                cursor.execute(
                    "INSERT INTO tipotransaccion (Descripcion) VALUES (%s)", (tipotransaccion,))
                db.commit()
                IDTipoTransaccion= cursor.lastrowid
            else:
                IDTipoTransaccion= IDTipoTransaccion[0]

            cursor.execute(
                "UPDATE cuentas SET Saldo = Saldo - %s WHERE NumeroCuenta = %s",( Valor, CuentaOrigen))
            cursor.execute(
                "UPDATE cuentas SET Saldo = Saldo + %s WHERE NumeroCuenta = %s",( Valor, cuenta_destino))
            cursor.execute("INSERT INTO movimientos (Valor,NumeroCuenta,CuentaOrigen,IDTipoTransaccion)VALUES (%s,%s,%s, %s)",(Valor, cuenta_destino, CuentaOrigen, IDTipoTransaccion))
            db.commit()
            mensaje = "Transaccion realizada exitosamente."
        else:
            mensaje="saldo insuficiente"
        cursor.close()
        return render_template("transacciones.html", mensaje=mensaje)
    else:
        return render_template("transacciones.html")



    
    

    



        
        















if  __name__=='__main__':
    app.run(debug=True)