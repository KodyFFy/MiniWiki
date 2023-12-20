import tkinter as tk
from tkinter import END, TclError, messagebox
from tkinter import filedialog  
from tkinter import ttk
from tkinter import font

import sqlite3 as sql

import pathlib
import tkinter

from PIL import Image, ImageTk
import io

import configparser as cfg


class miniWiki:
	
	def __init__(self, window: tk.Tk, configFile: pathlib.Path):

		self.config = cfg.ConfigParser()
		self.configFile = pathlib.Path(configFile)
		self.configExists = self.checkCfg()

		if self.configExists:
			self.config.read(self.configFile)
			self.getConfigData()
		else:
			self.createCfg()
			self.config.read(self.configFile)
			self.getConfigData()

		self.window = window
		self.window.title("Википедия знаменитых конструкторов РФ")
		self.window.geometry(self.resolution)
		self.window.resizable(width=False, height=False)

		self.createMenuBars()
		self.creatHelpBar()

		self.switch = False
		
		self.photoPath = 1

		self.readDb()

		self.windowListbox.selection_set(0)
		self.dataVisual(None)

	def checkCfg(self):
		return self.configFile.exists()

	def createCfg(self):
		with self.configFile.open(mode='w') as configFile:
			configFile.write("""
[Settings]
\nResolution = 1279x750
\nDefaultPhoto = 404.jpg
\nEditorKey = 777
\nDefaultDbPath = WikiDb.db
			""")

	def getConfigData(self):
		self.resolution = self.config.get("Settings", "Resolution")
		self.defaultPhoto = self.config.get("Settings", "DefaultPhoto")
		self.editorKey = self.config.get("Settings", "EditorKey")
		self.defaultDbPath = self.config.get("Settings", "DefaultDbPath")
		return

	def createMenuBars(self):
		bars = tk.Menu(self.window)

		upperBarFund = tk.Menu(bars, tearoff=0)
		
		bars.add_cascade(label="Wiki", menu=upperBarFund)

		upperBarFund.add_command(label="Найти", command=self.search, accelerator="Ctrl+F")
		upperBarFund.add_separator()
		upperBarFund.add_command(label="Добавить", command=self.insertInfo, accelerator="F2")
		upperBarFund.add_command(label="Изменить", command=self.editInfo, accelerator="Ctrl+F2")
		upperBarFund.add_command(label="Удалить", command=self.deleteObject, accelerator="F3")
		upperBarFund.add_separator()
		upperBarFund.add_command(label="Выход", command=self.closeApp, accelerator="F4")

		self.window.bind("<F1>", lambda event: self.Content())
		self.window.bind("<F2>", lambda event: self.insertInfo())
		self.window.bind("<Control-F2>", lambda event: self.editInfo())
		self.window.bind("<F3>", lambda event: self.deleteObject())
		self.window.bind("<F4>", lambda event: self.closeApp())
		self.window.bind("<Control-f>", lambda event: self.search())

		upperBarReference = tk.Menu(bars, tearoff=0)

		bars.add_cascade(label="Справка", menu=upperBarReference)

		upperBarReference.add_command(label="Содержание", command=self.Content, accelerator="F1")
		upperBarReference.add_command(label="О программе", command=self.aboutApp)

		self.window.config(menu=bars)

	def creatHelpBar(self):
		self.helpBar = tk.Label(self.window, text="F1 - Содержание, F2 - Добавить, Ctrl+F2 - Изменить, F3 - Удалить,  F4 - Закрыть, Ctrl+F - Поиск", relief=tk.SUNKEN, anchor=tk.W)
		self.helpBar.pack(side=tk.BOTTOM, fill=tk.X)

	def aboutApp(self):
		tk.messagebox.showinfo("О программе", "Карманная Wiki об знаменитых конструкторов РФ\n(с) Dobrin V.P., 2023")

	def Content(self):
		if self.switch is False:
			self.switch = True

			self.contentWindow = tk.Toplevel(self.window)
			self.contentWindow.title("Содержание")
			self.contentWindow.geometry("440x100")
			self.contentWindow.resizable(width=False, height=False)

			labelInfo = tk.Label(self.contentWindow,font=('Arial', 16),text="База данных 'Знаменитых консрукторах РФ'\nПозволяет: \nДобовлять/Изменять/Удалять информацию.")
			labelInfo.place(x=0,y=0)

			self.contentWindow.protocol("WM_DELETE_WINDOW", self.turnSwitch)
		else:
			messagebox.showinfo("Уведомление", "Окно 'Содержание' уже открыто!")

	def closeApp(self):
		self.window.destroy()
		
	def turnSwitch(self):
		self.switch = False
		if self.contentWindow:
			self.contentWindow.destroy()
		else:
			return

	def readDb(self):

		self.dbCreater()

		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		data = cur.execute("""SELECT Name FROM WikiData""").fetchall()

		self.windowListbox = tk.Listbox(self.window, font=("Arial",10))
		self.windowListbox.place(x=0,y=0,width=250,height=729)

		self.windowPhotoLabel = tk.Label(self.window)
		self.windowPhotoLabel.place(x=250,y=50,width=600,height=600)

		self.windowEntery = tk.Text(self.window)
		self.windowEntery.place(x=848,y=0,width=430,height=729)

		for name in data:
			self.windowListbox.insert(END, name[0])
		
		self.windowListbox.bind("<ButtonRelease-1>", self.dataVisual)

		connect.close()

	def dataVisual(self, event):

		self.windowListbox.update_idletasks()
		
		try:
			selectName = self.windowListbox.curselection()
			selectName = self.windowListbox.get(selectName)

			connect = sql.connect(self.defaultDbPath)

			cur = connect.cursor()

			info = cur.execute("""
			SELECT Info FROM WikiData WHERE Name = ?
			""", (selectName,)).fetchall()[0][0]

			photo = cur.execute("""
			SELECT Photo FROM WikiData WHERE Name = ?
			""", (selectName,)).fetchall()[0][0]

			photo = Image.open(io.BytesIO(photo)).resize((600,600), resample=Image.Resampling.BILINEAR)
			photo = ImageTk.PhotoImage(photo)

			self.windowPhotoLabel.configure(image=photo)
			self.windowPhotoLabel.image = photo


			self.windowEntery.delete("1.0", tk.END)
			self.windowEntery.insert('1.0',info)
			
		except:
			
			pass
		
	def dbCreater(self):
		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		cur.execute("""
		CREATE TABLE IF NOT EXISTS WikiData(
		Name TEXT NOT NULL,
		Info TEXT NOT NULL,
		Photo BLOB NOT NULL
		)
		""")

		connect.close()
		return

	def insertInfo(self):

		if self.editorKey == "777":
			self.insertWindow = tk.Toplevel(self.window)
			self.insertWindow.title("Редактор БД. Режим добавления")
			self.insertWindow.geometry("600x600")
			self.insertWindow.resizable(width=False, height=False)

			fioLabel = tk.Label(self.insertWindow, text = "Введите ФИО",font=16)
			fioLabel.place(x=0,y=30,width=599,height=41)

			self.fioEnter = tk.Text(self.insertWindow, font=16)
			self.fioEnter.place(x=0,y=70,width=598,height=64)

			infoLabel = tk.Label(self.insertWindow, text = "Введите информацию",font=16)
			infoLabel.place(x=0,y=140,width=598,height=64)

			self.infoEnter = tk.Text(self.insertWindow, font=16)
			self.infoEnter.place(x=0,y=210,width=599,height=168)

			searchButton = tk.Button(self.insertWindow, text = "Выбрать фото", command=self.getPath, font=16)
			searchButton.place(x=460,y=380,width=137,height=109)

			passButton = tk.Button(self.insertWindow, text = "Добавить", command=self.addToData, font=16)
			passButton.place(x=0,y=490,width=312,height=110)

			exitButton = tk.Button(self.insertWindow, text = "Отмена/Закрыть", command=self.closeInsertWindow, font=16)
			exitButton.place(x=310,y=490,width=312,height=110)
		else:
			messagebox.showinfo("Ошибка доступа!", "У вас нет доступа к этой функции")

	def closeInsertWindow(self):
		self.insertWindow.destroy()

	def getPath(self):
		filetypes = (('Png фотография', '*.png'),('Jpg фотография', '*.jpg'))
				
		f = filedialog.askopenfile(filetypes=filetypes, initialdir="C:/Downloads")

		think = 0
		workWindow = 0

		try:
			self.insertWindow.deiconify()
			think = 0
		except:
			self.editWindow.deiconify()
			think = 1

		if think == 0:
			workWindow = self.insertWindow
		elif think == 1:
			workWindow = self.editWindow
		
		if f is not None:
			self.photoPath = f.name
			photo = Image.open(self.photoPath).resize((100,100), resample=Image.Resampling.BILINEAR)
			photo = ImageTk.PhotoImage(photo)
			if think == 0:
				self.photoLabel = tk.Label(workWindow, image=photo)
				self.photoLabel.image = photo
				self.photoLabel.place(x=170,y=385)
			elif think == 1:
				self.photoReLabel = tk.Label(workWindow, image=photo)
				self.photoReLabel.image = photo
				self.photoReLabel.place(x=170,y=385)

	def addToData(self):
		fio = self.fioEnter.get("1.0", tk.END).strip()
		info = self.infoEnter.get("1.0", tk.END).strip()

		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		if fio.strip() == "":
			messagebox.showinfo("Ошибка!", "Вы не указали ФИО")
			connect.close()
			return
		elif info.strip() == "":
			info = "Информацию не указали"

		try:
			with open(self.photoPath, 'rb') as file:
				photo = file.read().strip()
		except:
			with open(self.defaultPhoto, 'rb') as file:
				photo = file.read().strip()

		
		cur.execute("""INSERT INTO WikiData (Name, Info, Photo) VALUES (?,?,?)""", (fio, info, photo))

		cur.close()

		connect.commit()

		connect.close()

		self.insertWindow.destroy()
		self.photoPath = None
		self.windowListbox.insert(END, fio)

	def editInfo(self):
		if self.editorKey == "777":
			self.editWindow = tk.Toplevel(self.window)
			self.editWindow.title("Редактор БД. Режим изменения")
			self.editWindow.geometry("600x600")
			self.editWindow.resizable(width=False, height=False)

			connect = sql.connect(self.defaultDbPath)

			cur = connect.cursor()
		
			targets = list(cur.execute("""
			SELECT Name FROM WikiData
			""").fetchall())

			targets = [item[0].split() for item in targets]

			self.choiceEditName = None

			self.choicer = ttk.Combobox(self.editWindow, values=targets)
			self.choicer.place(x=0,y=0, width=200, height=20)
			self.choicer.set("Кого редактируем?")
			self.choicer.bind("<<ComboboxSelected>>", self.targetChange)

			connect.close()

			fioLabel = tk.Label(self.editWindow, text = "Введите ФИО",font=16)
			fioLabel.place(x=0,y=30,width=599,height=41)

			self.fioReEnter = tk.Text(self.editWindow, font=16)
			self.fioReEnter.place(x=0,y=70,width=598,height=64)

			infoLabel = tk.Label(self.editWindow, text = "Введите информацию",font=16)
			infoLabel.place(x=0,y=140,width=598,height=64)

			self.infoReEnter = tk.Text(self.editWindow, font=16)
			self.infoReEnter.place(x=0,y=210,width=599,height=168)

			searchButton = tk.Button(self.editWindow, text = "Выбрать фото", command=self.getPath, font=16)
			searchButton.place(x=460,y=380,width=137,height=109)

			passButton = tk.Button(self.editWindow, text = "Изменить", command=self.updateData, font=16)
			passButton.place(x=0,y=490,width=312,height=110)
	
			exitButton = tk.Button(self.editWindow, text = "Отмена/Закрыть", command=self.closeEdittWindow, font=16)
			exitButton.place(x=310,y=490,width=312,height=110)
		else:
			messagebox.showinfo("Ошибка доступа!", "У вас нет доступа к этой функции")

	def targetChange(self, event):
		self.choiceEditName = self.choicer.get()

		if self.choiceEditName == "Кого редактируем?":
			messagebox.showinfo("Уведомление", "Вы не выбрали объект для редактирования")
			self.choiceEditName = None
			return

		self.fioReEnter.delete("1.0", tk.END)
		self.fioReEnter.insert('1.0',self.choiceEditName)

		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		info = cur.execute("""
		SELECT Info FROM WikiData WHERE Name = (?)
		""", (self.choiceEditName,)).fetchall()[0][0]

		
		self.infoReEnter.delete("1.0", tk.END)
		self.infoReEnter.insert('1.0',info)

		photo = cur.execute("""
		SELECT Photo FROM WikiData WHERE Name = (?)
		""", (self.choiceEditName,)).fetchall()[0][0]

		photo = Image.open(io.BytesIO(photo)).resize((100,100), resample=Image.Resampling.BILINEAR)
		photo = ImageTk.PhotoImage(photo)

		self.photoReLabel = tk.Label(self.editWindow, image=photo)
		self.photoReLabel.image = photo
		self.photoReLabel.place(x=170,y=385)

		connect.close()

	def updateData(self):
		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		name = self.choiceEditName
		if name is None or name == "":
			messagebox.showinfo("Уведомление", "Вы не выбрали объект редактирования")
			self.editWindow.deiconify()
			connect.close()
			return

		newName = self.fioReEnter.get('1.0', tk.END).strip()
		newInfo = self.infoReEnter.get('1.0', tk.END).strip()

		oldPhoto = cur.execute("""SELECT Photo FROM WikiData WHERE Name = ?""", (name,)).fetchall()[0][0].strip()

		i = 0
		for nameObject in self.windowListbox.get(0, tk.END):
			if name == nameObject:
				_id = i
				self.windowListbox.delete(_id)
				self.windowListbox.insert(END,newName)
				self.windowListbox.update_idletasks()
				break
			i+=1
		try:
			with open(self.photoPath, 'rb') as file:
				newPhoto = file.read().strip()
		except:
			newPhoto = oldPhoto

		if newName.strip() == "":
			messagebox.showinfo("Ошибка!", "Вы не указали ФИО")
			self.editWindow.deiconify()
			connect.close()
			return
		elif newInfo.strip() == "":
			newInfo = "Информацию не указали"
			
		if oldPhoto == newPhoto:
			cur.execute("""UPDATE WikiData SET Name = ?, Info = ?, Photo = ? WHERE Name = (?)""",(newName, newInfo, oldPhoto, name))
		else:
			cur.execute("""UPDATE WikiData SET Name = ?, Info = ?, Photo = ? WHERE Name = (?)""",(newName, newInfo, newPhoto, name))

		cur.close()

		connect.commit()

		connect.close()

		self.photoPath = None
		self.editWindow.destroy()

	def closeEdittWindow(self):
		self.editWindow.destroy()

	def deleteObject(self):
		if self.editorKey == "777":
			self.deleteWindow = tk.Toplevel(self.window)
			self.deleteWindow.title("Редактор БД. Режим удаления записей")
			self.deleteWindow.geometry("400x300")
			self.deleteWindow.resizable(width=False, height=False)

			connect = sql.connect(self.defaultDbPath)

			cur = connect.cursor()
		
			targets = list(cur.execute("""
			SELECT Name FROM WikiData
			""").fetchall())

			targets = [item[0].split() for item in targets]

			self.choicerDeleter = ttk.Combobox(self.deleteWindow, values=targets)
			self.choicerDeleter.place(x=0,y=0, width=400, height=30)
			self.choicerDeleter.set("Кого удаляем?")

			passButton = tk.Button(self.deleteWindow, text = "Удалить", command=self.delData)
			passButton.place(x=0,y=260,width=140,height=40)
	
			exitButton = tk.Button(self.deleteWindow, text = "Отмена/Закрыть", command=self.closeEdittWindow)
			exitButton.place(x=260,y=260,width=140,height=40)

			self.windowListbox.selection_clear(0, tk.END)
			self.windowListbox.selection_set(0)
			self.dataVisual(None)

		else:
			messagebox.showinfo("Ошибка доступа!", "У вас нет доступа к этой функции")

	def closeEdittWindow(self):
		self.deleteWindow.destroy()

	def delData(self):
		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		name = self.choicerDeleter.get()

		if name == "Кого удаляем?" or name == "":
			messagebox.showinfo("Уведомление", "Вы не выбрали объект для удаления")
			self.deleteWindow.deiconify()
			connect.close()
			return

		quest = messagebox.askquestion(f"Подтверждение действия", f"Вы уверены что хотите удалить объект {name}?")

		if quest == "yes" or quest == "да":

			cur.execute("""
			DELETE FROM WikiData WHERE Name = ?
			""", (name,))

			targets = list(cur.execute("""
			SELECT Name FROM WikiData
			""").fetchall())

			targets = [item[0].split() for item in targets]
			self.choicerDeleter.set("Кого удаляем?")
			self.choicerDeleter.configure(values=targets)

			self.deleteWindow.deiconify()

			messagebox.showinfo("Уведомление", "Запись успешно удалена!")
			i = 0
		for nameObject in self.windowListbox.get(0, tk.END):
			if name == nameObject:
				_id = i
				self.windowListbox.delete(_id)
				self.windowListbox.update_idletasks()
				break
			i+=1
		if quest == "no" or quest == "нет":
			connect.close()
			return

		connect.commit()

		connect.close()

	def search(self):
		self.searchWindow = tk.Toplevel(self.window)
		self.searchWindow.title("Поиск")
		self.searchWindow.geometry("300x100")
		self.searchWindow.resizable(width=False, height=False)	

		self.searchEntry = tk.Entry(self.searchWindow,font=("Arial",12))
		self.searchEntry.place(x=0,y=30,width=300,height=30)
		self.searchEntry.bind("<Return>", self.onSearch)
		self.searchEntry.bind("<FocusIn>", self.clear)
		self.searchEntry.insert(0, "Введите запрос и нажмите Enter")

	def clear(self, event):
		self.searchEntry.delete(0, tk.END)

	def onSearch(self, event):

		connect = sql.connect(self.defaultDbPath)

		cur = connect.cursor()

		seartchWord = self.searchEntry.get()

		self.window.deiconify()

		data = cur.execute("""
		SELECT Name, Info FROM WikiData
		""")

		for dat in data:
			name = dat[0]
			info = dat[1]

			i = 0
			if seartchWord in info:
				for nameObject in self.windowListbox.get(0, tk.END):
					if name == nameObject:
						_id = i
						listbox = self.windowListbox
						listbox.selection_clear(0, tk.END)
						listbox.selection_set(_id)
						self.dataVisual(None)
						self.searchWindow.destroy()
						connect.close()
						return
					i+=1

		self.searchWindow.destroy()
		messagebox.showinfo("Уведомление", "Ничего не найдено")
		connect.close()


if __name__ == "__main__":
	window = tk.Tk()
	#path = pathlib.Path(r"WikiDb.db")
	cfgPath = pathlib.Path(r"wiki.cfg")
	app = miniWiki(window,cfgPath)
	window.mainloop()
	
