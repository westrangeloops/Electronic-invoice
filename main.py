from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import uic
from datetime import datetime
import pandas as pd
import sqlite3


# Create database
conn = sqlite3.connect('BrooklynDataBase.sql')
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS transactions (Servicio tinytext, Precio number, Puesto tinytext, Brooklyn number'
           ', PagarPuesto number, Insumo number, Comision number, Fecha datetime, M_Pago tinytext)')
conn.commit()
# Global objects:
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
print(dt_string)
# Load to the GUI the dataframe
price_data = pd.read_csv('Brooklyndata.csv')
savedataframe = pd.DataFrame()
# Search
# Qt5 must have a class everytime:


class BrooklynGUI(QDialog):

    def __init__(self):
        super(BrooklynGUI, self).__init__()
        uic.loadUi("BrooklynGUI.ui", self)
        self.show()

        global price_data
        # Load most common shortcuts
        zero = str(price_data.iloc[0]['Servicio'])
        one = str(price_data.iloc[1]['Servicio'])
        two = str(price_data.iloc[2]['Servicio'])
        three = str(price_data.iloc[3]['Servicio'])
        four = str(price_data.iloc[4]['Servicio'])
        # Create most common labels
        self.servicio0.setText(str(zero))
        self.servicio1.setText(str(one))
        self.servicio2.setText(str(two))
        self.servicio3.setText(str(three))
        self.servicio4.setText(str(four))
        # Buttons for stock services.
        self.stockbutton0.clicked.connect(lambda: self.mappend(zero))
        self.stockbutton1.clicked.connect(lambda: self.mappend(one))
        self.stockbutton2.clicked.connect(lambda: self.mappend(two))
        self.stockbutton3.clicked.connect(lambda: self.mappend(three))
        self.stockbutton4.clicked.connect(lambda: self.mappend(four))
        # Load to the list all services
        self.ListaServicios.setSelectionMode(QAbstractItemView.MultiSelection)
        listservices = [price_data.iloc[i]['Servicio'] for i in range(4, price_data.shape[0])]
        self.ListaServicios.addItems(listservices)
        # Agregar de la lista todos los seleccionados:
        self.AgregarLista.clicked.connect(lambda: self.lista_services())
        # Buttons for special services:
        self.AgregarEspecial.clicked.connect(lambda: self.special_services())
        #  Last item erase button
        self.Eliminar.clicked.connect(lambda: self.erase_last_service())
        # Erase all:
        self.NuevaOrden.clicked.connect(lambda: self.erase_order())
        # Save button to Pandas to SQL
        self.SaveOrder.clicked.connect(lambda: self.save_order())
        # Admin login
        self.LogInButton.clicked.connect(self.login)
        # Set monospace fonts
        self.ResumenOrden.setFont(QtGui.QFont("Monospace"))
        # Generate the
        self.GenerarInforme.clicked.connect(lambda: self.generar_informe())

    def login(self):
        if self.AdminName.text() == 'Dubal' and self.AdminPass.text() == 'Africa2018':
            # self.EscribeAlgo.setEnabled(True)
            pass

        else:
            message = QMessageBox()
            message.setText("Usuario o contraseña incorrecta")
            message.exec_()

    def save_order(self):
        global savedataframe
        # First assign to the order date and pay method
        savedataframe['Fecha'] = dt_string
        savedataframe['M_Pago'] = self.LectorMetPago.currentText()
        # Sum Brooklyn to for shop and erease.

        # Save to sql
        print(savedataframe)
        savedataframe.to_sql('transactions', conn, if_exists='append', index=False)

        # Erase the columns after save in sql
        savedataframe = savedataframe.drop('Fecha', axis=1)
        savedataframe = savedataframe.drop('M_Pago', axis=1)
        self.erase_order()


    def mappend(self, service):
        global savedataframe
        global price_data

        # Manage variables reading from Brooklyndata.csv
        try:
            puesto = self.LectorPuesto.currentText()
            precio = price_data[price_data['Servicio'] == '{}'.format(service)]['Precio'].iloc[0]
            comision = price_data[price_data['Servicio'] == '{}'.format(service)]['Comision'].iloc[0]
            insumo = price_data[price_data['Servicio'] == '{}'.format(service)]['Insumo'].iloc[0]
            preciof = precio - insumo
            if puesto == 'Brooklyn':
                pagarpuesto = 0
            else:
                pagarpuesto = preciof * (comision / 100)
            forshop = preciof - pagarpuesto

        except IndexError:
            lst_append = service

        else:
            lst_append = [service, precio, puesto, forshop, pagarpuesto, insumo, comision]

        # Fixed values to make the dict
        dict_columns = ['Servicio', 'Precio', 'Puesto', 'Brooklyn', 'PagarPuesto', 'Insumo', 'Comision']

        # From lst_append received for different program buttons: create dict to append
        dict_to_append = {dict_columns[i]: lst_append[i] for i in range(len(lst_append))}

        # dict to append
        dtdict = pd.DataFrame(dict_to_append, index=[0])
        df = pd.concat([savedataframe, dtdict], ignore_index=True)
        df.reset_index()
        # save data frame
        savedataframe = df
        self.graphic()

    def graphic(self):
        global savedataframe
        # Total
        total = savedataframe['Precio'].sum()
        self.Total.setText(str(total))
        self.ResumenOrden.setText(savedataframe[['Servicio', 'Precio', 'Puesto']].to_string(index=False))
        print(savedataframe)
        print(total)

    def special_services(self):
        global price_data
        servicio = str(self.NombreServicio.toPlainText()).upper()
        if servicio != '':
            puesto = self.LectorPuesto.currentText()
            insumo = int(self.PrecioInsumo.toPlainText())
            precio = int(self.PrecioServicio.toPlainText())

            if puesto == 'Brooklyn':
                pagarpuesto = 0
            else:
                pagarpuesto = (precio - insumo) * 0.6 + insumo

            forshop = (precio - insumo) * 0.4
            special = [servicio, precio, puesto, forshop, pagarpuesto, insumo]
            self.mappend(special)


    def lista_services(self):
        global price_data
        services = self.ListaServicios.selectedItems()
        lservices = [self.ListaServicios.selectedItems()[i].text() for i in range(len(services))]
        for service in lservices:
            self.mappend(service)
        self.ListaServicios.clearSelection()

    def erase_last_service(self):
        global savedataframe
        if len(savedataframe.index) >= 0:
            savedataframe = savedataframe.iloc[:-1, :]
            self.graphic()
        else:
            pass

    def erase_order(self):
        global savedataframe
        savedataframe = savedataframe.iloc[0:0]
        self.graphic()

    def generar_informe(self):
        try:
            # Get time from the calendars
            beggintime = str(self.BeginTime.selectedDate().toPyDate()) + " 00:00:00"
            endtime = str(self.EndTime.selectedDate().toPyDate()) + " 23:99:99"

            # Summary to pay each
            sqlpuestos = "SELECT Puesto, SUM(PagarPuesto) FROM Transactions WHERE Fecha BETWEEN '{}' AND '{}' GROUP BY Puesto "\
                .format(beggintime, endtime)
            df1 = pd.read_sql_query(sqlpuestos, conn)
            # Get shop sum
            db.execute('SELECT SUM(Brooklyn) AS total_brooklyn FROM transactions')
            total_brooklyn = db.fetchone()[0]
            df1.at[0, 'SUM(PagarPuesto)'] = float(total_brooklyn)

            # Save to csv
            df1.to_csv('PAGOPUESTO {} TO {}.csv'.format(beggintime.strip(" 00:00:00"), endtime.strip(" 23:99:99")))

            # Shop always wins
            sqlalldata = "SELECT * FROM Transactions WHERE Fecha BETWEEN '{}' AND '{}' ".format(beggintime, endtime)
            dfcsv = pd.read_sql_query(sqlalldata, conn)
            dfcsv.to_csv('INFORME {} TO {}.csv'.format(beggintime.strip(" 00:00:00"), endtime.strip(" 23:99:99")))

        except TypeError:
            print('Empty')
        else:
            print(df1)



def main():
    app = QApplication([])
    window = BrooklynGUI()
    app.exec_()


if __name__ == '__main__':
    main()
