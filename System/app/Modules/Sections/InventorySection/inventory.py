import flet as ft
import constants
from Modules.customControls import CustomAnimatedContainerSwitcher, CustomNavigationOptions, CustomAnimatedContainer, CustomFloatingActionButton, CustomSnackBar
from Modules.Sections.InventorySection.products_components import ProductInfo, ProductContainer, FilterByName
from Modules.Sections.InventorySection.combos_components import ComboInfo, ComboContainer
from Modules.Sections.InventorySection.categories_components import CategoryInfo, CategoryContainer
from Modules.categories_modules import CategoryForm
from Modules.products_module import ProductForm
from Modules.combos_module import ComboForm
from DataBase.crud.category import getCategories
from DataBase.crud.product import getProducts
from DataBase.crud.combo import getCombos
from config import getDB
from utils.imageManager import ImageManager
from utils.sessionManager import isAdmin

class Inventory(ft.Stack):
  def __init__(self, page):
    super().__init__()
    self.expand = True
    self.page = page
    
    self.categoryButton = CustomNavigationOptions(
      icon=ft.Icons.CATEGORY_ROUNDED,
      text="Categorías",
      function=lambda e: self.selectView(self.categoryButton),
      color="#666666",
      focusedColor=constants.BLACK,
      opacityInitial=1,
      highlightColor=None,
      contentAlignment=ft.MainAxisAlignment.CENTER,
    )
    
    self.productButton = CustomNavigationOptions(
      icon=ft.Icons.COFFEE_ROUNDED,
      text="Productos",
      function=lambda e: self.selectView(self.productButton),
      color="#666666",
      focusedColor=constants.BLACK,
      opacityInitial=1,
      highlightColor=None,
      contentAlignment=ft.MainAxisAlignment.CENTER,
      default=True,
    )
    
    self.comboButton = CustomNavigationOptions(
      icon=ft.Icons.FASTFOOD_ROUNDED,
      text="Combos",
      function=lambda e: self.selectView(self.comboButton),
      color="#666666",
      focusedColor=constants.BLACK,
      opacityInitial=1,
      highlightColor=None,
      contentAlignment=ft.MainAxisAlignment.CENTER,
    )
    
    self.topNavigationBar = ft.Container(
      margin=ft.margin.symmetric(horizontal=20, vertical=10),
      bgcolor=ft.Colors.TRANSPARENT,
      height=60,
      width=600,
      content=ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
        spacing=20,
        controls=[
          self.categoryButton,
          self.productButton, 
          self.comboButton,
        ]
      )
    )
    
    self.categoryInitialContent = ft.Column(
      alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      expand=True,
      controls=[
        ft.Text(
          value="Selecciona una categoría para ver más información",
          color=constants.BLACK,
          size=32,
          weight=ft.FontWeight.W_700,
          text_align=ft.TextAlign.CENTER,
        )
      ]
    )
    
    self.productInitialContent = ft.Column(
      alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      expand=True,
      controls=[
        ft.Text(
          value="Selecciona un producto para ver más información",
          color=constants.BLACK,
          size=32,
          weight=ft.FontWeight.W_700,
          text_align=ft.TextAlign.CENTER,
        )
      ]
    )
    
    self.comboInitialContent = ft.Column(
      alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      expand=True,
      controls=[
        ft.Text(
          value="Selecciona un combo para ver más información",
          color=constants.BLACK,
          size=32,
          weight=ft.FontWeight.W_700,
          text_align=ft.TextAlign.CENTER,
        )
      ]
    )
    
    self.infoContainer = CustomAnimatedContainerSwitcher(
      content=ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
          self.productInitialContent
        ]  
      ),
      expand=True,
      col={"sm": 12, "md": 12, "lg": 8, "xl": 7}
    )
    
    self.addItemButton = CustomFloatingActionButton(on_click=self.addItemForm)
    
    self.controlSelected = None

    self.selected = self.productButton
    
    initialContent = self.getProductsToFill()
    self.items = initialContent
    self.itemsContainer = CustomAnimatedContainerSwitcher(
      shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=5,
        color=constants.BLACK_INK,
      ),
      padding=0,
      content=ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
        height=800,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
          self.createFilter(),
          ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            controls=initialContent,
          )
        ]
      ),
      height=None,
      width=None,
      expand=True,
      col={"sm": 12, "md": 9, "lg": 4, "xl": 5},
    )
    
    self.controls = [
      ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
          self.topNavigationBar,
          ft.ResponsiveRow(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            run_spacing=10,
            controls=[
              self.itemsContainer,
              self.infoContainer,
            ]
          ),
        ]
      ),
      ft.Container(
        content=self.addItemButton if isAdmin() else None,
        right=10,
        bottom=10,
      )
    ]
    
  def selectView(self, target):
    if not self.selected == target:
      self.selected.deselectOption()
      self.selected = target
      self.selected.selectOption()
      
      self.resetCurrentView()
  
  def resetInfoContainer(self):
    self.infoContainer.changeStyle(height=150, width=300, shadow=None)
    
    if self.selected == self.categoryButton:
      self.infoContainer.setNewContent(self.categoryInitialContent)
    elif self.selected == self.productButton:
      self.infoContainer.setNewContent(self.productInitialContent)
    elif self.selected == self.comboButton:
      self.infoContainer.setNewContent(self.comboInitialContent)
    
    self.controlSelected = None
    
  def addItemForm(self, e):
    self.newContent = None
    if self.selected == self.categoryButton:
      self.newContent = CategoryForm(self.page, self)
    elif self.selected == self.productButton:
      self.newContent = ProductForm(self.page, self)
    elif self.selected == self.comboButton:
      self.newContent = ComboForm(self.page, self)
      
    if not self.infoContainer.height == 800:
      self.infoContainer.changeStyle(height=800, width=700, shadow=ft.BoxShadow(
        blur_radius=5,
        spread_radius=1,
        color=constants.BLACK_INK,
      ))
    if self.newContent:
      if self.controlSelected:
        self.controlSelected.deselect()
        self.controlSelected = None
      self.infoContainer.setNewContent(self.newContent)
      
  def editItemForm(self, newContent):
    self.infoContainer.changeStyle(
      height=800,
      width=700,
      shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=5,
        color=constants.BLACK_INK,
      )
    )
    self.infoContainer.setNewContent(newContent)

  
  def fillItemsContainer(self):
    items = []
    
    if self.selected == self.categoryButton:
      items = self.getCategoriesToFill()
    elif self.selected == self.productButton:
      items = self.getProductsToFill()
    elif self.selected == self.comboButton:
      items = self.getCombosToFill()
    
    newContent = ft.Column(
      alignment=ft.MainAxisAlignment.CENTER,
      expand=True,
      height=800,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    self.items = items
    
    containersColumn = ft.Column(
      expand=True,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
      alignment=ft.MainAxisAlignment.CENTER,
      scroll=ft.ScrollMode.AUTO,
      controls=self.items,
    )
    
    newContent.controls = [self.createFilter(), containersColumn]
    self.itemsContainer.setNewContent(newContent)
  
  def filterData(self, value):
    try:
      print("Filtering...")
      filteredContainers = []
      value = value.lower().strip()
      
      if not value:
        for container in self.items:
          container.visible = True
        self.itemsContainer.update()
        return
      
      for container in self.items:
        if value in container.name.lower():
          container.visible = True
          filteredContainers.append(container)
        else:
          container.visible = False
      
      if len(filteredContainers) == 0:
        self.page.snack_bar = CustomSnackBar(page=self.page, text="No se han encontrado coincidencias")
        self.page.snack_bar.open = True
        self.page.update()
      self.itemsContainer.update()
      return filteredContainers
    except Exception as err: 
      raise Exception(f"Error during data filtering: {err}")
  
  def createFilter(self):
    if self.selected == self.productButton:
      bar_hint_text = "Buscar producto..."
      view_hint_text = "Escribe el nombre del producto..."
    elif self.selected == self.categoryButton:
      bar_hint_text = "Buscar categoría..."
      view_hint_text = "Escribe el nombre de la categoría..."
    else:
      bar_hint_text = "Buscar combo..."
      view_hint_text = "Escribe el nombre del combo..."
    
    self.filter = FilterByName(
      page=self.page, 
      controls=[],
      bar_hint_text=bar_hint_text,
      view_hint_text=view_hint_text,
      on_submit=lambda e: self.filterData(e.control.value),
    )
    
    return self.filter
  
  def getCategoriesToFill(self):
    try:
      with getDB() as db:
        categories = getCategories(db)
        containers = []
        imageManager = ImageManager()
        if len(categories) > 0:
          for category in categories:
            container = CategoryContainer(
              idCategory=category.idCategory,
              name=category.name,
              description=category.description,
              imgPath=imageManager.getImagePath(category.imgPath),
              infoContainer=self.infoContainer,
              mainContainer=self
            )
            
            containers.append(container)
        return containers

    except Exception as err:
      raise
    
  def getProductsToFill(self):
    try:
      with getDB() as db:
        products = getProducts(db)
        containers = []
        imageManager = ImageManager()
        if len(products) > 0:
          for product in products:
            container = ProductContainer(
              idProduct=product.idProduct,
              name=product.name,
              description=product.description,
              infoContainer=self.infoContainer,
              mainContainer=self,
              page=self.page,
              imgPath=imageManager.getImagePath(product.imgPath),
            )
            containers.append(container)
        return containers
    except Exception as err:
      raise
  
  def getCombosToFill(self):
    try:
      with getDB() as db:
        combos = getCombos(db)
        containers = []
        imageManager = ImageManager()
        
        if len(combos) > 0:
          for combo in combos:
            container = ComboContainer(
              idCombo=combo.idCombo,
              name=combo.name,
              infoContainer=self.infoContainer,
              mainContainer=self,
              page=self.page,
              imgPath=imageManager.getImagePath(combo.imgPath)
            )
            containers.append(container)
        return containers
    except Exception as err:
      raise
  
  def resetCurrentView(self):
    self.resetInfoContainer()
    self.fillItemsContainer()
    
  def textForEmptyContainer(self, message):
    return ft.Text(
      value=message,
      size=32,
      color=constants.BLACK,
      weight=ft.FontWeight.W_700,
      text_align=ft.TextAlign.CENTER,
    )
    
  def showNewInfoContent(self, content, controlSelected=None):
    if self.controlSelected:
      self.controlSelected.deselect()
    self.controlSelected = controlSelected
    self.controlSelected.select()
    
    if not self.infoContainer.height == 600:
      self.infoContainer.changeStyle(height=600, width=700, shadow=ft.BoxShadow(
        blur_radius=5,
        spread_radius=1,
        color=constants.BLACK_INK,
      ))
    self.infoContainer.setNewContent(content)
  
  def showLowStockProduct(self, idProduct):
    for container in self.itemsContainer.content.content.controls[1].controls:
      if container != self.filter and container.idProduct == idProduct and not container == self.controlSelected:
        newContent = ProductInfo(
          imgPath=container.imgPath,
          idProduct=idProduct,
          infoContainer=self.infoContainer,
          mainContainer=self,
          productContainer=self,
          page=self.page,
        )
        self.showNewInfoContent(newContent, container)
        break