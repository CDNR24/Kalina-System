import flet as ft
import constants
from Modules.customControls import CustomUserIcon, CustomOperationContainer, CustomTextField, CustomAnimatedContainer, CustomNavigationOptions, CustomFilledButton, CustomDropdown, CustomDeleteButton, CustomAlertDialog, CustomReturnButton, CustomOutlinedButton, CustomFilePicker
from config import getDB
from Modules.Sections.ClosingsSection.components.TransactionRecord import TransactionRecord
from DataBase.crud.closing import getClosingById
from DataBase.crud.sale import getSaleById
from utils.dateConversions import convertToLocalTz
from DataBase.crud.transaction import getTransactionById
from utils.dateConversions import getLocal
from datetime import datetime
from templates.closing.create import createPDF
from utils.sessionManager import getCurrentUser
from DataBase.crud.user import getUserByUsername
from DataBase.crud.combo import getComboByName
from DataBase.crud.product import getProductByName
from Modules.Sections.InventorySection.products_components import ProductContainer
from utils.imageManager import ImageManager
import locale

class ClosingRecord(ft.Container):
  def __init__(self, page, date, sales:[], productsName:{}, combosName:{}, amount, totals, gain, idClosing:int=None, partial=True, createFunction=None):
    super().__init__()
    self.page = page
    self.gain = gain
    self.date = date
    self.idClosing = idClosing
    self.amount = amount
    self.sales = sales
    self.productsName = productsName
    self.combosName = combosName
    self.totals = totals
    self.border_radius = 20
    self.partial = partial
    self.expand = True
    self.width = 800
    self.createFunction = createFunction
    
    with getDB() as db:
      self.saleObjects = [getSaleById(db, sale) for sale in self.sales]
      
      groupedTransactions = {
        method: [] for method in constants.methodIcons if method != "All"
      }
      
      for sale in self.saleObjects:
        transactions = sale.transactions
        
        for transaction in transactions:
          method = transaction.method.value
          groupedTransactions[method].append(transaction.idTransaction)
      
      self.transactions = groupedTransactions
    
    self.paymentContainers = [TransactionRecord(
      page=self.page, 
      transactionType="Pago",
      method=method,
      transactions=self.transactions[method],
      payments=totals["payments"].get(method, {"total": 0})["total"],
      changes=totals["changes"].get(method, {"total": 0})["total"],
      amount={
        "VES": totals["payments"].get(method, {"VES": 0})["VES"] - totals["changes"].get(method, {"VES": 0})["VES"],
        "USD": totals["payments"].get(method, {"USD": 0})["USD"] - totals["changes"].get(method, {"USD": 0})["USD"],
        "total": totals["payments"].get(method, {"total": 0})["total"] - totals["changes"].get(method, {"total": 0})["total"],
        },
      mainContainer=self,
    ) for method in list(constants.methodIcons.keys()) if method != "All"]
    
    with getDB() as db:
      self.productsContainers = []
      imageManager = ImageManager()
      for key, value in self.productsName.items():
        product = getProductByName(db, key)
        container = ProductContainer(
          idProduct=product.idProduct,
          name=product.name,
          description=f"{value} unidades",
          infoContainer=None,
          mainContainer=None,
          page=self.page, 
          imgPath=imageManager.getImagePath(product.imgPath),
        )
        container.margin = ft.margin.symmetric(vertical=3)
        container.on_click = None
        self.productsContainers.append(container)
      
      if len(self.productsContainers) == 0:
        self.productsContainers.append(ft.Row(
          expand=True,
          height=40,
          alignment=ft.MainAxisAlignment.CENTER,
          vertical_alignment=ft.CrossAxisAlignment.CENTER,
          controls=[
            ft.Text(
              value="No se han vendido productos",
              size=20,
              color=constants.RED_TEXT,
              weight=ft.FontWeight.W_600,
              text_align=ft.TextAlign.CENTER,
            )
          ]
        ))
    
    self.totalHeader = ft.Text(
      value=f"{round(self.amount, 2)}$",
      color=constants.GREEN_TEXT,
      size=28,
      weight=ft.FontWeight.W_700,
    )
    
    self.gainText = ft.Text(
      value=f"{round(self.gain, 2)}$",
      color=constants.ORANGE_TEXT,
      size=20,
      weight=ft.FontWeight.W_600,
    )
    
    self.dateText = ft.Text(
      value=f"{getLocal().strftime("%d/%m/%Y")}" if self.partial else f"{self.date}",
      color=constants.BLACK,
      size=20,
    )
    
    self.createClosingButton = ft.Container(
      content=CustomOutlinedButton(
        text="Crear cierre",
        clickFunction=self.createFunction,
      ),
      margin=ft.margin.symmetric(vertical=10)
    )
    
    self.filePicker = CustomFilePicker(
      page=self.page,
      on_result=self.getPath,
    )

    self.page.overlay.append(self.filePicker)
    
    self.downloadButton = ft.IconButton(
      icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
      on_click=lambda e: self.openFilePicker(),
      icon_size=32,
      icon_color=constants.BLACK,
    )
    
    self.incomeTitle = ft.Text(
      value="Resumen de ingresos",
      size=24, 
      color=constants.BLACK,
      weight=ft.FontWeight.W_600,
      text_align=ft.TextAlign.CENTER,
      height=50
    )
    
    self.inventoryTitle = ft.Text(
      value="Desglose de productos vendidos",
      size=24, 
      color=constants.BLACK,
      weight=ft.FontWeight.W_600,
      text_align=ft.TextAlign.CENTER,
      height=50,
    )
    
    closingContent = [
      self.incomeTitle,
      *self.paymentContainers,
      ft.Divider(color=constants.WHITE_GRAY),
      self.inventoryTitle,
      *self.productsContainers,
    ]
    
    if self.partial:
      closingContent.append(self.createClosingButton)
    else:
      with getDB() as db:
        closing = getClosingById(db, self.idClosing)
        closingContent.append(ft.Text(
          value=f"Realizado por: {closing.user.employee.name} {closing.user.employee.surname}",
          color=constants.BLACK,
          size=20,
        ))
      
    self.columnContent = ft.Column(
        expand=True,
        width=800,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
          ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
              ft.Text(
                value="Cierre de caja:" if not self.partial else "Cierre de caja parcial:",
                color=constants.BLACK,
                size=28,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
              ),
              self.totalHeader,
            ]  
          ),
          ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
              ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                  ft.Text(
                    value="Ganancia aproximada:",
                    color=constants.BLACK,
                    size=20,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                  ),
                  self.gainText,
                ]  
              ),
              ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                  ft.Text(
                    value="Fecha:",
                    color=constants.BLACK,
                    size=20,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                  ),
                  self.dateText,
                ]  
              ),
            ]
          ),
          ft.Divider(color=constants.BLACK_INK),
          ft.Column(
            expand=True,
            width=800,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=closingContent
          )
        ]
      )
    
    self.content = CustomAnimatedContainer(
      actualContent=ft.Stack(
        controls=[
          self.columnContent,
          ft.Container(
            right=10,
            top=0,
            content=self.downloadButton
          )
        ]
      )
    )
    
  def openFilePicker(self):
    try:
      if self.filePicker not in self.page.overlay:
        self.page.overlay.append(self.filePicker)
      self.page.update()
      self.filePicker.get_directory_path()
    except Exception as err:
      print(err)
      
  def getPath(self, e):
    try:
      with getDB() as db:
        closing = getClosingById(db, self.idClosing)
        user = getUserByUsername(db, getCurrentUser())
        date = closing.date.strftime("%A %d de %B del %Y, %H:%M:%S %p") if not self.partial else datetime.now().strftime("%A %d de %B del %Y, %H:%M:%S %p")
        # date = date.replace("AM", "am").replace("PM", "pm")
        if e.path:
          print("Selected path:", e.path)
          top5 = sorted(self.productsName.items(), key=lambda x: x[1], reverse=True)
          top5 = dict(top5[:5])
          result = createPDF(
            info={
              "title": "Cierre de caja parcial" if self.partial else "Cierre de caja",
              "employee": f"{user.employee.name} {user.employee.surname} {user.employee.secondSurname}" if self.partial else f"{closing.user.employee.name} {closing.user.employee.surname} {closing.user.employee.secondSurname}", 
              "closing_amount": f"{round(self.amount, 2)}",
              "estimated_gain": f"{round(self.gain, 2)}",
              "date": date,
              "rif": constants.companyInfo["rif"],
              "soldInventory": self.productsName,
              "top5": top5,
              "phone": constants.companyInfo["phone"],
              "email": constants.companyInfo["email"],
              "payment_methods": {
                method: round(self.totals["payments"].get(method, {"total": 0})["total"] - self.totals["changes"].get(method, {"total": 0})["total"], 2) for method in constants.methodIcons.keys() if method != "All"  
              },
            },
            outputPath=e.path,
          )
          
          if result:
            dialog = CustomAlertDialog(
              title="PDF creado exitosamente",
              modal=False,
            )
            self.page.open(dialog)
    except:
      dialog = CustomAlertDialog(
        title="No se creó el PDF",
        content=ft.Text(
          value="Algo salió mal",
          size=20,
          color=constants.BLACK,
        ),
        modal=False,
      )
      self.page.open(dialog)
      raise
  
  def changeContent(self, newContent, method):
    if len(self.transactions[method]) == 0:
      dialog = CustomAlertDialog(
        title="No se han realizado transacciones de este tipo",
        content=None,
        modal=False,
      )
      self.page.open(dialog)
    else:
      oldContent = self.content.content
      
      newContent = ft.Stack(
        expand=True,
        controls=[
          newContent,
          ft.Container(
            left=0,
            top=0,
            content=CustomReturnButton(
              function=lambda e: self.content.setNewContent(oldContent)
            )
          )
        ]
      )
      self.content.setNewContent(newContent)
  
  def showFurtherInfo(self, newContent):
    self.otherOldContent = self.content.content
    
    newContent = ft.Stack(
      expand=True,
      controls=[
        newContent,
        ft.Container(
          top=0,
          left=0,
          border_radius=5,
          bgcolor=constants.WHITE,
          content=CustomReturnButton(
            function=lambda e: self.content.setNewContent(self.otherOldContent)
          ),
        )
      ]
    )
    
    self.content.setNewContent(newContent)
    
  def showSale(self, newContent):
    previousContent = self.content.content
    
    newContent = ft.Stack(
      expand=True,
      controls=[
        newContent,
        ft.Container(
          left=0,
          top=0,
          border_radius=5,
          bgcolor=constants.WHITE,
          content=CustomReturnButton(
            function=lambda e: self.content.setNewContent(previousContent)
          )
        )
      ]
    )
    
    self.content.setNewContent(newContent=newContent)