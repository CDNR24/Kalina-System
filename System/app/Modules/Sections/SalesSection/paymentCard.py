import flet as ft
import constants
from Modules.customControls import CustomAlertDialog, CustomAnimatedContainer, CustomAnimatedContainerSwitcher, CustomOperationContainer, CustomTextField, CustomDropdown, CustomImageContainer, CustomFloatingActionButton, CustomFilledButton, CustomTooltip, CustomReturnButton, CustomEditButton, CustomExchangeDialog 
from Modules.transaction_module import TransactionForm
from utils.exchangeManager import exchangeRateManager
from exceptions import InvalidData, DataAlreadyExists, DataNotFoundError
from utils.saleManager import saleMakerManager


class PaymentCard(ft.Container):
  def __init__(self, page, formContainer, height=140, width=140):
    super().__init__()
    self.page = page
    self.formContainer = formContainer
    self.expand = True
    
    self.bgcolor = constants.WHITE
    self.border = ft.border.all(2, constants.BLACK_GRAY)
    self.border_radius = 20
    self.padding = ft.padding.all(10)
    self.ink = True
    self.ink_color = constants.WHITE_GRAY
    self.on_click = lambda e: self.clickFunction()
    
    self.price = 0
    
    self.selectedPayments = []
    
    self.paymentAmountText = ft.Text(
      value=0,
      size=20,
      color=constants.GREEN_TEXT,
      weight=ft.FontWeight.W_700,
      overflow=ft.TextOverflow.ELLIPSIS,
    )
    
    self.withoutPayment = ft.Row(
      alignment=ft.MainAxisAlignment.CENTER,
      vertical_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        ft.Icon(
          name=ft.Icons.ADD_CARD,
          size=32,
          color=constants.GREEN_TEXT,
        ),
        ft.Text(
          value="Agregar pagos",
          size=20,
          color=constants.BLACK,
          text_align=ft.TextAlign.CENTER,
          overflow=ft.TextOverflow.ELLIPSIS,
        )
      ]
    )
    
    self.withPayment = ft.Row(
      alignment=ft.MainAxisAlignment.CENTER,
      vertical_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        ft.Icon(
          name=ft.Icons.INPUT,
          size=32,
          color=constants.GREEN_TEXT,  
        ),
        ft.Text(
          value="Monto total:",
          color=constants.BLACK,
          size=20,
        ),
        self.paymentAmountText,
      ]
    )
    
    self.animatedContainer = CustomAnimatedContainer(
      actualContent=self.withoutPayment
    )
    
    self.content = ft.Column(
      expand=True,
      alignment=ft.MainAxisAlignment.CENTER,
      controls=[
        self.animatedContainer
      ]  
    )
    
  def clickFunction(self):
    try:
      self.itemsSelector = saleMakerManager.itemsSelector
      print(self.itemsSelector)
      if self.itemsSelector.validateAllItemFields():
        exchangeRate = exchangeRateManager.getRate()
        if exchangeRate:
          newContent = TransactionManager(
            page=self.page,
            paymentCard=self,
            formContainer=self.formContainer,
            selectedPayments=self.selectedPayments,
          )
          
          self.formContainer.changeContent(newContent)
        else:
          dialog = CustomExchangeDialog(page=self.page)
          self.page.open(dialog)
    
    except InvalidData as e:
      dialog = CustomAlertDialog(
        modal=False,
        title="Datos incompletos",
        content=ft.Text(
          value=str(e),
          color=constants.BLACK,
          size=20,
        )
      )
      self.page.open(dialog)
    except:
      raise
  
  def validateCard(self):
    try:
      if len(self.selectedPayments) > 0:
        return True, self.selectedPayments, f"Monto total entrante: {self.price}$ / {self.price*exchangeRateManager.getRate()}Bs"
      else:
        raise InvalidData("Por favor, anexa los pagos entrantes de la venta.")
    except:
      raise
    
  def calculateTotal(self):
    try:
      exchangeRate = exchangeRateManager.getRate()
      self.price = 0
      if exchangeRate:
        for payment in self.selectedPayments:
          amount = payment["amount"]
          if payment["currency"] == "Bs":
            amount = payment["amount"]/exchangeRate
          self.price += amount
        self.price = round(self.price, 2)
      else:
        self.price = 0
        dialog = CustomAlertDialog(
          modal=False,
          title="No se ha establecido la tasa de intercambio.",
          content=None
        )
        self.page.open(dialog)
    except:
      raise
    
  def updateCard(self, transactions:list=[]):
    try:
      self.calculateTotal()
      
      self.paymentAmountText.value = f"{round(self.price,2)}$"
      
      if self.price > 0:
        self.animatedContainer.setNewContent(self.withPayment)
      else:
        self.animatedContainer.setNewContent(self.withoutPayment)
    except:
      raise
  
  def updateAboutRate(self, newRate):
    try:
      self.updateCard(self.selectedPayments)
    except:
      pass
  
  def calculateTotal(self):
    try:
      exchangeRate = exchangeRateManager.getRate()
      self.price = 0
      if exchangeRate:
        for payment in self.selectedPayments:
          amount = payment["amount"]
          if payment["currency"] == "Bs":
            amount = payment["amount"]/exchangeRate
          self.price += amount
      self.price = round(self.price, 2)
      return self.price
    except: 
      raise
  

class TransactionManager(ft.Container):
  def __init__(self, page, paymentCard, formContainer, selectedPayments=[], transactionType="Pago"):
    super().__init__()
    self.page = page
    self.paymentCard = paymentCard
    self.formContainer = formContainer
    self.selectedPayments = selectedPayments
    self.transactionType = transactionType
    
    self.alignment = ft.alignment.center
    self.expand = True
    
    self.titleText = ft.Text(
      value="Pagos de la venta" if self.transactionType == "Pago" else "Vueltos de la venta",
      size=32,
      color=constants.BLACK,
      weight=ft.FontWeight.W_700,
      text_align=ft.TextAlign.CENTER,
    )
    
    self.salePrice = ft.Text(
      value=f"Precio de la venta: {round(self.formContainer.priceCard.price, 2)}$ / {round(self.formContainer.priceCard.price*exchangeRateManager.getRate(), 2)}Bs" if self.transactionType == "Pago" else f"Cambio pendiente: {round(self.formContainer.calculateTotalChange(), 2)}$ / {round(self.formContainer.calculateTotalChange()*exchangeRateManager.getRate(), 2)}Bs",
      color=constants.BLACK,
      size=20,
      text_align=ft.TextAlign.CENTER,
    )
    
    self.createPaymentButton = CustomEditButton(
      function=lambda e: self.showTransactionForm(),
    )
    self.createPaymentButton.content.name = ft.Icons.ADD_CARD_ROUNDED
    
    self.paymentDefaultContainer = ft.Column(
      expand=True,
      alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        ft.Icon(
          name=ft.Icons.CREDIT_CARD_OFF_OUTLINED,
          size=32,
          color=constants.BLACK,
        ),
        ft.Text(
          value="No se ha registrado ningún pago" if self.transactionType == "Pago" else "No se ha registrado ningún vuelto",
          size=20,
          color=constants.BLACK,
          text_align=ft.TextAlign.CENTER,
          overflow=ft.TextOverflow.ELLIPSIS,
        )
      ]
    )
    
    self.finishButton = CustomFilledButton(
      text="Finalizar",
      clickFunction=lambda e: self.finishFunction(),
    )
  
    self.animatedPaymentContainer = ft.Container(
      border=ft.border.all(2, constants.BLACK),
      padding=ft.padding.symmetric(horizontal=5, vertical=10),
      expand=True,
      border_radius=20,
      alignment=ft.alignment.center,
      content=CustomAnimatedContainer(
        actualContent=self.getPaymentsList() if len(self.selectedPayments) > 0 else self.paymentDefaultContainer
      )
    )
    
    self.columnMainContent = ft.Column(
      expand=True,
      alignment=ft.MainAxisAlignment.CENTER,
      spacing=20,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        ft.Row(
          alignment=ft.MainAxisAlignment.CENTER,
          controls=[
            ft.Text(
              value="Agregar pago" if self.transactionType == "Pago" else "Agregar vuelto",
              size=20,
              color=constants.BLACK,
            ),
            self.createPaymentButton,
          ]
        ),
        self.animatedPaymentContainer,
        self.finishButton,
      ]
    )
    
    self.managerContent = ft.Column(
      expand=True,
      alignment=ft.MainAxisAlignment.CENTER,
      spacing=20,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        self.titleText,
        self.salePrice,
        self.columnMainContent,
      ]
    )
    
    self.animatedMainContainer = CustomAnimatedContainer(
      actualContent=self.managerContent,
    )
    
    self.content = self.animatedMainContainer
    
  def showTransactionForm(self):
    try:
      form = TransactionForm(
        page=self.page,
        calculateChange=self.paymentCard.calculateChange if self.transactionType == "Cambio" else None,
        previousContainer=self,
        formContainer=self.formContainer,
        transactionType=self.transactionType,
      )
      
      form = ft.Stack(
        expand=True,
        controls=[
          form,
          ft.Container(
            left=10,
            top=10,
            content=CustomReturnButton(
              function=lambda e: self.returnToManager()
            )
          )
        ]
      )
      
      self.animatedMainContainer.setNewContent(form)
    except:
      raise
  
  def returnToManager(self):
    self.animatedMainContainer.setNewContent(self.managerContent)
  
  def getTransactionRecord(self, paymentInfo):
    try:
      transactionRecord = TransactionRecord(
        page=self.page,
        paymentInfo=paymentInfo,
        deleteFunction=self.removePaymentFromList,
      )
      
      return transactionRecord
    except:
      raise
  
  def addPaymentToList(self, paymentInfo):
    try:
      self.selectedPayments.append(paymentInfo)
      for payment in self.selectedPayments:
        print(payment)
    except:
      raise
  
  def removePaymentFromList(self, paymentInfo, transactionRecord):
    try:
      
      self.selectedPayments.remove(paymentInfo)
      self.animatedPaymentContainer.content.content.controls.remove(transactionRecord)
      
      if len(self.animatedPaymentContainer.content.content.controls) == 0:
        self.animatedPaymentContainer.content.setNewContent(self.paymentDefaultContainer)
      else:
        self.animatedPaymentContainer.content.update()
    except:
      raise
    
  def getPaymentsList(self):
    try:
      newContent = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[]
      )
      
      for paymentInfo in self.selectedPayments:
        record = self.getTransactionRecord(paymentInfo)
        newContent.controls.append(record)
      
      return newContent
    except:
      raise
    
  def showPayments(self, paymentInfo=None):
    try:
      self.returnToManager()
        
      if paymentInfo:
        self.addPaymentToList(paymentInfo)
        
      self.animatedPaymentContainer.content.setNewContent(self.getPaymentsList())
    except:
      raise
    
  def finishFunction(self):
    try:
      self.formContainer.returnToBegin() 
      self.paymentCard.updateCard(transactions=self.selectedPayments)
    except:
      raise
  
  def calculateTotal(self):
    try:
      exchangeRate = exchangeRateManager.getRate()
      self.price = 0
      if exchangeRate:
        for change in self.selectedPayments:
          amount = change["amount"]
          if change["currency"] == "Bs":
            amount = change["amount"]/exchangeRate
          self.price += amount
      return self.price
    except:
      raise
    
class TransactionRecord(ft.Container):
  def __init__(self, page, paymentInfo, deleteFunction=None):
    super().__init__()
    self.page = page
    self.paymentInfo = paymentInfo
    self.method = self.paymentInfo["method"]
    self.amount = self.paymentInfo["amount"]
    self.currency = self.paymentInfo["currency"]
    self.reference = self.paymentInfo["reference"]
    self.transactionType = self.paymentInfo["transactionType"]
    self.deleteFunction = deleteFunction
    
    self.shadow = ft.BoxShadow(
      spread_radius=1,
      blur_radius=1,
      color=constants.WHITE_GRAY,
    )
    self.bgcolor = constants.WHITE
    self.padding = ft.padding.symmetric(horizontal=10, vertical=20)
    self.border_radius = ft.border_radius.all(30)
    
    self.methodText = ft.Text(
      value=self.method,
      size=24,
      color=constants.BLACK,
      weight=ft.FontWeight.W_500,
      overflow=ft.TextOverflow.ELLIPSIS,
    )
    
    print(self.method, constants.methodIcons[self.method])
    self.methodRow = ft.Row(
      vertical_alignment=ft.CrossAxisAlignment.CENTER,
      controls=[
        ft.Icon(
          name=constants.methodIcons[self.method],
          size=32,
          color=constants.BLACK
        ),
        self.methodText,
      ]
    )
    
    self.amountText = ft.Text(
      value=f"{self.amount}{self.currency}",
      size=28,
      weight=ft.FontWeight.W_700,
      color=constants.GREEN_TEXT if self.transactionType == "Pago" else constants.RED_TEXT,
      overflow=ft.TextOverflow.ELLIPSIS,
    )
    
    if self.deleteFunction:
      self.deleteButton = CustomEditButton(
        function=lambda e: self.deleteFunction(paymentInfo=self.paymentInfo, transactionRecord=self),
      )
      self.deleteButton.content.name = ft.Icons.DELETE_ROUNDED
    
    self.content = ft.Row(
      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
      vertical_alignment=ft.CrossAxisAlignment.CENTER,
      expand=True,
      controls=[
        self.methodRow,
        ft.Row(
          vertical_alignment=ft.CrossAxisAlignment.CENTER,
          controls=[self.amountText] if not self.deleteFunction else [self.amountText, self.deleteButton]
        ),
      ]
    )