import flet as ft 
from Modules.customControls import CustomFilledButton, CustomOutlinedButton, CustomCheckbox, CustomReturnButton, CustomSimpleContainer, CustomTextField, CustomDropdown, CustomAnimatedContainer, CustomOperationContainer
from validation import evaluateForm
import constants
from interface import showLogin
import time
from utils.pathUtils import getImagePath
from DataBase.crud.employee import getEmployeeById
from DataBase.crud.user import createUser, getUserByUsername, queryUserData, getUsers
from DataBase.crud.recovery import createRecovery
from config import getDB
from exceptions import DataNotFoundError, DataAlreadyExists, InvalidData
import threading

class RegisterForm(CustomSimpleContainer):
  def __init__(self, page, login=True):
    super().__init__()
    self.page = page
    self.login = login
    
    self.button = ft.Row(
      controls=[
        CustomOutlinedButton(text="Siguiente", clickFunction=lambda e: self.advance()),
      ], 
      alignment=ft.MainAxisAlignment.CENTER
    )

    self.titleRegister = ft.Row(
      controls=[
        ft.Text(value="Nuevo Usuario", size=42, color=constants.BLACK, weight=ft.FontWeight.BOLD)
      ],
      alignment=ft.MainAxisAlignment.CENTER
    )

    self.newUserName = CustomTextField(
      label="Nombre de nuevo usuario",
      revealPassword=True,
      mode="light",
      hint_text=None,
      field="username",
      expand=False,
      submitFunction=lambda e: self.advance()
    )
    
    self.password = CustomTextField(
      label="Contraseña",
      revealPassword=True,
      mode="light",
      hint_text=None,
      field="password",
      expand=1,
      submitFunction=lambda e: self.advance()
    )
    
    self.passwordConfirmation = CustomTextField(
      label="Contraseña",
      revealPassword=False,
      mode="light",
      hint_text=None,
      field="password",
      expand=1,
      submitFunction=lambda e: self.advance()
    )
    
    self.userCI = CustomTextField(
      label="Documento de Empleado",
      revealPassword=True,
      mode="light",
      hint_text=None,
      field="ci",
      expand=False,
      submitFunction=lambda e: self.advance()
    )

    # inputs
    self.inputs = ft.Column(
      expand=True,
      alignment=ft.MainAxisAlignment.CENTER,
      controls=[
        self.newUserName,
        self.userCI,
        ft.Row(
          controls=[
            self.password,
            self.passwordConfirmation,
          ],
        )
      ],
    )
    
    # checkbox
    self.checkbox = CustomCheckbox(label="Usuario Administrador", fill_color=constants.BROWN, color=constants.BLACK)
    
    self.helpText = ft.Row(
      alignment=ft.MainAxisAlignment.CENTER,
      controls=[
        ft.Icon(
          name=ft.icons.HELP_ROUNDED,
          color=constants.BLACK,
        ),
        ft.Text(
          value="¿Cuáles son los requisitos de contraseña?",
          size=20,
          color=constants.BLACK,
          tooltip=ft.Tooltip(
            message="La contraseña debe tener:\n• Una letra mayúscula.\n• Una letra minúscula.\n• Un número.\n• Un símbolo.\n• Un máximo de 25 caracteres.\n• Un mínimo de 8 caracteres.",
            padding=20,
            border_radius=10,
            text_style=ft.TextStyle(
              color=constants.BLACK,
              size=20,
            ),
            bgcolor=constants.WHITE,
            border=ft.border.all(2, color=constants.BLACK),
          )
        )
      ]
    )
    
    self.formFirst = ft.Column(
      expand=True,
      controls=[
        self.titleRegister,
        self.helpText,
        self.inputs,
        ft.Row(
          controls=[self.checkbox] if not self.existOneAdmin() else [],
          alignment=ft.MainAxisAlignment.CENTER
        ),
        self.button,
      ],
      alignment=ft.MainAxisAlignment.CENTER,
      spacing=20,
    )

    ####################

    self.questionOne = CustomDropdown(
      label="Primera pregunta",
      options=constants.dropdownOne,
      mode="light"
    )
    
    self.answerOne = CustomTextField(
      label="Respuesta",
      mode="light",
      hint_text=None,
      revealPassword=True,
      field="others",
      expand=False,
      submitFunction=lambda e: self.advance()
    )
    
    self.questionTwo = CustomDropdown(
      label="Segunda pregunta",
      options=constants.dropdownTwo,
      mode="light"
    )
    
    self.answerTwo = CustomTextField(
      label="Respuesta",
      mode="light",
      hint_text=None,
      revealPassword=True,
      field="others",
      expand=False,
      submitFunction=lambda e: self.advance()
    )

    self.questionsInputs = ft.Column(
      expand=True,
      controls=[
        self.questionOne,
        self.answerOne,
        self.questionTwo,
        self.answerTwo
      ],
      alignment=ft.MainAxisAlignment.CENTER
    )
    
    self.backButton = CustomReturnButton(function=self.back, color=constants.BLACK, size=30)

    self.finishButton = ft.Row(
      controls=[
        CustomFilledButton(text="Crear Usuario", clickFunction=lambda e: self.advance())
      ],
      alignment=ft.MainAxisAlignment.CENTER
    )
    
    self.secondContent = ft.Column(
      expand=True,
      controls=[
        ft.Row(
          controls=[
            ft.Icon(
              name=ft.icons.HELP_OUTLINED,
              color=constants.BROWN,
            ),
            ft.Text(value="Preguntas de Seguridad", size=18, color=constants.BLACK),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
          vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        self.questionsInputs,
        self.button
      ],
      alignment=ft.MainAxisAlignment.CENTER,
      spacing=20,
    )
    
    self.formSecond = ft.Stack(
      expand=True,
      controls=[
        self.secondContent,
        ft.Container(
          content=self.backButton,
          margin=ft.margin.only(top=0, left=0),
          alignment=ft.alignment.top_left,
          width=60,
          height=60,
        )
      ]
    )
    
    #####
    
    self.adminUsernameField = CustomTextField(
      label="Nombre de usuario",
      field="username",
      submitFunction=lambda e: self.advance(),
    )
    self.adminPasswordField = CustomTextField(
      label="Contraseña",
      field="password",
      submitFunction=lambda e: self.advance()
    )
    self.thirdContent = ft.Column(
      expand=True,
      controls=[
        ft.Column(
          expand=True,
          alignment=ft.MainAxisAlignment.CENTER,
          spacing=20,
          controls=[
            ft.Row(
              alignment=ft.MainAxisAlignment.CENTER,
              controls=[
                ft.Icon(
                  name=ft.icons.HELP_OUTLINED,
                  color=constants.BLACK,
                ),
                ft.Text(
                  value="Confirmación de un usuario administrador",
                  color=constants.BLACK,
                  size=18,
                )
              ]
            ),
            ft.Column(
              controls=[
                self.adminUsernameField,
                self.adminPasswordField,
              ]
            ),
          ]
        ),
        self.finishButton,
      ],
      alignment=ft.MainAxisAlignment.CENTER,
    )
    
    self.formThird = ft.Stack(
      expand=True,
      controls=[
        self.thirdContent,
        ft.Container(
          content=self.backButton,
          margin=ft.margin.only(top=0, left=0),
          alignment=ft.alignment.top_left,
          width=60,
          height=60,
        )
      ]
    )
    
    # Final
    
    self.formList = [self.formFirst, self.formSecond, self.formThird]
    self.currentForm = 0
    
    self.animatedContainer = CustomAnimatedContainer(
      actualContent=self.formList[self.currentForm],
      transition=ft.AnimatedSwitcherTransition.FADE,
      duration=300,
      reverse_duration=200,
    )
    
    self.operation = CustomOperationContainer(
      operationContent=self.animatedContainer,
      mode="light"
    )
    
    # content
    self.content = self.operation
    
  def existOneAdmin(self):
    count = 0
    with getDB() as db:
      users = getUsers(db)
      for user in users:
        if user.role == "Administrador":
          count += 1
      return count > 0
    
  def advance(self):
    isValid = True
    try:
      if self.animatedContainer.content == self.formFirst:
        isValid = evaluateForm(username=[self.newUserName], ci=[self.userCI], password=[self.password, self.passwordConfirmation])
        
        if isValid and not self.password.value == self.passwordConfirmation.value:
          isValid = False
          self.operation.actionFailed("Las contraseñas no coinciden.")
          threading.Timer(1.5, self.operation.restartContainer).start()
        else:
          with getDB() as db:
            user = getUserByUsername(db, self.newUserName.value.strip())
            if user:
              isValid = False
              raise DataAlreadyExists("Nombre de usuario en uso.")
            employee = getEmployeeById(db, int(self.userCI.value))
            if not employee:
              isValid = False
              raise DataNotFoundError("El documento no existe.")
            elif employee.user:
              isValid = False
              raise DataAlreadyExists("El empleado ya posee usuario.")

      elif self.animatedContainer.content == self.formSecond:
        isValid = evaluateForm(others=[self.questionOne, self.questionTwo, self.answerOne, self.answerTwo])
      else:
        isValid = evaluateForm(username=[self.adminUsernameField], password=[self.adminPasswordField])
        
        with getDB() as db:
          if isValid:
            if queryUserData(db, username=self.adminUsernameField.value.strip(), password=self.adminPasswordField.value.strip()):
              role = "Administrador" if self.checkbox.value == True else "Colaborador"
              
              user = createUser(
                db=db,
                username=self.newUserName.value.strip(),
                password=self.password.value.strip(),
                role=role,
                ciEmployee=self.userCI.value.strip(), 
              )
              recovery = createRecovery(
                db=db,
                questionOne=self.questionOne.value.strip(),
                answerOne=self.answerOne.value.strip(),
                questionTwo=self.questionTwo.value.strip(),
                answerTwo=self.answerTwo.value.strip(),
                idUser=user.idUser,
              )
              
              self.operation.actionSuccess("Usuario creado")
              if self.login:
                threading.Timer(1.5, lambda: showLogin(self.page)).start()
              else: 
                return True
            else:
              raise InvalidData("Contraseña incorrecta.")
            
      if not isValid:
        print("Campos inválidos")
      else:
        print("Campos válidos")
        if self.currentForm < len(self.formList) - 1:
          self.currentForm += 1
          self.animatedContainer.setNewContent(self.formList[self.currentForm])
          return False
    except InvalidData as err:
      self.operation.actionFailed(err)
      threading.Timer(1.5, self.operation.restartContainer).start()
    except DataAlreadyExists as err:
      self.operation.actionFailed(err)
      threading.Timer(1.5, self.operation.restartContainer).start()
    except DataNotFoundError as err:
      self.operation.actionFailed(err)
      threading.Timer(1.5, self.operation.restartContainer).start()
    except Exception as err:
      print(err)
      raise
    
  def back(self, e):
    if self.currentForm > 0:
      self.currentForm -= 1
      self.animatedContainer.setNewContent(self.formList[self.currentForm])

class RegisterPresentation(CustomSimpleContainer):
  def __init__(self, page):
    super().__init__(gradient=True)
    self.spacing = 20
    self.page = page
    
    self.logo = ft.Image(
      src=getImagePath("logoReg-kalinaSystem.png"),
      fit="contain",
      width=180,
      height=180
    )
    
    self.title = ft.Text(
      value="Bienvenido a bordo", 
      size=42, 
      color=constants.WHITE, 
      weight=ft.FontWeight.BOLD,
      text_align=ft.TextAlign.CENTER
    )
    
    self.description = ft.Text(
      value="Regístrate y disfruta de una experiencia personalizada. Nos alegra tenerte aquí",
      color=constants.WHITE, 
      size=18,
      weight=ft.FontWeight.BOLD,
      text_align=ft.TextAlign.CENTER
    )
    
    self.button = CustomFilledButton(
      text="¿Ya tienes un usuario?",
      overlay=constants.ORANGE_OVERLAY,
      bgcolor=constants.ORANGE,
      color=constants.BLACK,
      clickFunction=lambda e: showLogin(self.page)
    )
    
    self.login = ft.Row(
      controls=[
        self.button
      ],
      alignment=ft.MainAxisAlignment.CENTER
    )
    
    self.content = ft.Column(
      controls=[
        self.title,
        self.logo,
        self.login,
        self.description
      ],
      alignment=ft.MainAxisAlignment.CENTER,
      horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
class Register(ft.Row):
  def __init__(self, page):
    super().__init__()
    self.page = page
    self.spacing = 0
    
    self.controls = [
      RegisterForm(self.page),
      RegisterPresentation(self.page),
    ]