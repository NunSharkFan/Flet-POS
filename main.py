import flet
from functools import reduce
from typing import Callable
from datetime import datetime

class Account:
    def __init__(self, id: str, password: str):
        self.id = id
        self.password = password

class Product:
    def __init__(self, id: int, name: str, price: float, in_stock: int, image: str):
        self.id = id
        self.name = name
        self.price = price
        self.in_stock = in_stock
        self.image = image

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def subtotal(self):
        return self.product.price * self.quantity

class SaleOrder:
    def __init__(self, cashier: str, dt: str, total: float, cash: float, change: float, items: list[CartItem]):
        self.cashier = cashier
        self.dt = dt
        self.total = total
        self.cash = cash
        self.change = change
        self.items = items

accounts: list[Account] = []
with open("accounts.txt") as file: # TO BE USED WHEN CHECKING FOR MATCHING ACCOUNTS
    for line in file:
        if "*" in line:
            continue
        line.strip()
        Id = line[len("ID:"):line.index("PASS:")].strip()
        Pass = line[(line.index("PASS:") + len("PASS:")):].strip()
        accounts.append(Account(Id, Pass))

def refreshProducts():
    products: list[Product] = []
    with open("products.txt") as file: # THIS IS WHERE I FILL THE PRODUCTS IN I GUESS(?)
        for line in file:
            if "*" in line:
                continue
            line.strip()
            Id = int(line[len("ID:"):line.index("NAME:")].strip())
            Name = line[(line.index("NAME:") + len("NAME:")):(line.index("PRICE:"))].strip()
            Price = float(line[(line.index("PRICE:") + len("PRICE:")):(line.index("IN:"))].strip())
            In_Stock = int(line[(line.index("IN:") + len("IN:")):(line.index("IMAGE:"))].strip())
            Image = Pass = line[(line.index("IMAGE:") + len("IMAGE:")):].strip()
            products.append(Product(Id, Name, Price, In_Stock, Image))
    return products

appName = "Nun Shark Coding" # THIS IS THE APP NAME YEAH AS IT SAYS RIGHT THERE
# NOW YOU MAY BE WONDERING, WHY IS THIS HERE AND NOT WITH PASSTXTFIELD THINGY... THAT'S ACTUALLY A GOOD QUESTION
# WELL THE ANSWER IS THAT THIS IS THE ONLY WAY I CAN THINK OF, WHERE I CAN STILL MAKE USE OF THIS THINGS VALUE
userTxtField = flet.TextField(label = "Username")

def main(page : flet.Page):
    page.title = appName
    page.theme_mode = flet.ThemeMode.LIGHT
    
    def theme_change(_):
        if page.theme_mode == flet.ThemeMode.LIGHT:
            page.theme_mode = flet.ThemeMode.DARK
            theme_button.icon = flet.icons.DARK_MODE_OUTLINED
            page.update()
        else:
            page.theme_mode = flet.ThemeMode.LIGHT
            theme_button.icon = flet.icons.LIGHT_MODE_OUTLINED
            page.update()

    theme_button = flet.IconButton(icon = flet.icons.LIGHT_MODE_OUTLINED,
                                   on_click = theme_change)

    def route_change(route):
        page.views.clear() # THE WAY WE GO WITH WHAT WE SEE IS FIRST CLEAR EVERYTHING ON SCREEN THEN ADD STUFF IN ACCORDANCE TO ROUTE
        
        # AUTH PAGE, LOG IN FEATURE WILL BE HERE
        if page.route == "/auth":
            def authenticate_account(_):
                for account in accounts:
                    if userTxtField.value == account.id and passTxtField.value == account.password:
                        page.go("/main")
                        break
                else:
                    page.snack_bar = flet.SnackBar(content = flet.Text("Username or Password is Incorrect",
                                                                       color = "ff0000"),
                                                   bgcolor = "ffcccb")
                    page.snack_bar.open = True
                page.update()
            
            passTxtField = flet.TextField(label = "Password",
                                          password = True,
                                          can_reveal_password = True)

            page.views.append(flet.View(route = "/auth",
                                        appbar = flet.AppBar(title = flet.Row(controls = [flet.Text("Is This Not Nun Shark",
                                                                                                    expand = True),
                                                                                          theme_button]),
                                                             bgcolor = flet.colors.BLUE_200),
                                        vertical_alignment = flet.MainAxisAlignment.CENTER,
                                        horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                        controls = [flet.Text(appName,
                                                              size = 30),
                                                    userTxtField,
                                                    passTxtField,
                                                    flet.FilledButton(text = "Log In",
                                                                      on_click = authenticate_account)]))
            
        # MAIN PAGE, WHERE, AFTER LOGGING IN, YOU GET TO CHOOSE WHETHER TO START NEW TRANSAC, CHECK TRANSACS, OR LOG OUT
        elif page.route == "/main":

            def createCard(text, icon, route):
                return flet.Container(padding = 10,
                                      width = 200,
                                      height = 200,
                                      bgcolor = flet.colors.GREEN_200,
                                      on_click = route,
                                      content = flet.Column([flet.Icon(icon,
                                                                       size = 64),
                                                             flet.Text(text)],
                                                            alignment = flet.MainAxisAlignment.CENTER,
                                                            horizontal_alignment = flet.CrossAxisAlignment.CENTER))
            
            storeCard = createCard(text = "New Transaction",
                                   icon = flet.icons.ADD_OUTLINED,
                                   route = lambda _: page.go('/store'))
            
            historyCard = createCard(text = "Transaction History",
                                     icon = flet.icons.BOOK_OUTLINED,
                                     route = lambda _: page.go("/history"))

            exitCard = createCard(text = "Log Out",
                                  icon = flet.icons.LOGOUT_OUTLINED,
                                  route = lambda _: page.go('/auth'))

            page.views.append(flet.View(route = "/main",
                                        appbar = flet.AppBar(title = flet.Row(controls = [flet.Text(value = f'Welcome Back, {userTxtField.value}!',
                                                                                                    expand = True),
                                                                                          theme_button]),
                                                             bgcolor = flet.colors.BLUE_200),
                                        vertical_alignment = flet.MainAxisAlignment.CENTER,
                                        horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                        controls = [flet.Row(vertical_alignment = flet.CrossAxisAlignment.CENTER,
                                                             alignment = flet.MainAxisAlignment.CENTER,
                                                             controls = [storeCard,
                                                                         historyCard,
                                                                         exitCard])]))
        
        # THE PAGE YOU THOUGHT POS WAS ALL ABOUT.... THE BUY BUY THINGY PAGE
        elif page.route == "/store":
            products = refreshProducts()
            productMatcher = refreshProducts()
            cartItems: list[CartItem] = []
            total: float = reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)
            
            totalText = flet.Text(value = f'P {total}',
                                  weight = flet.FontWeight.W_900,
                                  size = 30)

            product_cards = flet.GridView(expand = 1,
                                          runs_count = 5,
                                          max_extent = 300,
                                          spacing = 5,
                                          run_spacing = 5)

            cartListView = flet.ListView()

            def addTransaction(x: int):
                now = datetime.now()
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                total = reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)
                with open('transactions.txt', 'a') as file:
                    transactionDetails = ""
                    transactionDetails += ('CASHIER:' + userTxtField.value).ljust(20)
                    transactionDetails += ('DATETIME:' + dt_string).ljust(30)
                    transactionDetails += ('TOTAL:' + str(total)).ljust(15)
                    transactionDetails += ('CASH:' + str(x)).ljust(15)
                    transactionDetails += ('CHANGE:' + str(x - total)).ljust(15)
                    for item in cartItems:
                        transactionDetails += ('[NAME:' + item.product.name + 'PRICE:' + str(item.product.price) + 'QTY:' + str(item.quantity) + 'SUBTOTAL:' + str(item.subtotal()) +']')
                    transactionDetails += '\n'
                    file.write(transactionDetails)

            def updateProductsTxt():
                toWrite = []
                with open('products.txt') as file:
                    for line in file:
                        if '*' in line:
                            toWrite.append(line)
                for item in products:
                    Id = ('ID:' + str(products.index(item))).ljust(10)
                    Name = ('NAME:' + (item.name)).ljust(50)
                    Price = ('PRICE:' + str(item.price)).ljust(15)
                    In_Stock = ('IN:' + str(item.in_stock)).ljust(10)
                    Image = 'IMAGE:' + item.image

                    toWrite.append(Id+Name+Price+In_Stock+Image+'\n')
                with open('products.txt', 'w') as file:
                    for line in toWrite:
                        file.write(line)

            def select_product(x: int):
                orgItem = products[x]

                def checkQuantity(_):
                    if quantityField.value == "":
                        subtotalText.value = f'P 0.00'
                        return
                    elif not quantityField.value.isnumeric():
                        quantityField.value = ""
                        subtotalText.value = f'P 0.00'
                    elif int(quantityField.value) < 0:
                        quantityField.value = ""
                        subtotalText.value = f'P 0.00'
                    elif int(quantityField.value) > orgItem.in_stock:
                        quantityField.value = orgItem.in_stock
                        subtotalText.value = f'P {int(quantityField.value)*orgItem.price}'
                    else:
                        subtotalText.value = f'P {int(quantityField.value)*orgItem.price}'
                    subtotalText.update()
                    page.update()

                quantityField = flet.TextField(value = '1',
                                               on_change = checkQuantity)
                subtotalText = flet.Text(f'P {orgItem.price}',
                                         weight = flet.FontWeight.BOLD,
                                         size = 24)
                
                def on_close(_):
                    dialog.open = False
                    dialog.update()

                def on_confirm(_):
                    if quantityField.value == "":
                        quantityField.value = "0"
                        subtotalText.value = f"P 0.00"
                    elif int(quantityField.value) == 0:
                        return
                    else:
                        for r in range(len(cartItems)):
                            if cartItems[r].product.id == orgItem.id:
                                cartItems[r].quantity += int(quantityField.value)
                                products[x].in_stock -= int(quantityField.value)
                                break
                        else:
                            cartItems.append(CartItem(orgItem, int(quantityField.value)))
                            products[x].in_stock = orgItem.in_stock - int(quantityField.value)
                        totalText.value = f'P {reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)}'
                        set_product_cards()
                        cartListShow()
                        on_close("")
                    page.update()
                
                dialog: flet.AlertDialog = flet.AlertDialog(title = flet.Text(f'{orgItem.name}   -  P{orgItem.price}   - {orgItem.in_stock} In Stock'),
                                                            content = flet.Container(width = 600,
                                                                                     height = 600,
                                                                                     content = flet.Column(alignment = flet.MainAxisAlignment.CENTER,
                                                                                                           horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                                                                                           controls = [flet.Image(src = orgItem.image,
                                                                                                                                  width = 400,
                                                                                                                                  height = 400,
                                                                                                                                  fit = True),
                                                                                                                       flet.Row(alignment = flet.MainAxisAlignment.CENTER,
                                                                                                                                controls = [quantityField]),
                                                                                                                       subtotalText])),
                                                            actions_alignment = flet.MainAxisAlignment.END,
                                                            actions = [flet.TextButton('CANCEL',
                                                                                       on_click = on_close),
                                                                       flet.TextButton('CONFIRM',
                                                                                       on_click = on_confirm)])

                page.dialog = dialog
                dialog.open = True
                page.update()

            def ItemCard(product:Product, click: Callable):
                return flet.Container(bgcolor = flet.colors.YELLOW_700,
                                      border_radius = 5,
                                      padding = 20,
                                      margin = 2,
                                      on_click = lambda _: click(),
                                      content = flet.Column(horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                                            alignment = flet.MainAxisAlignment.CENTER,
                                                            controls = [flet.Image(src = product.image,
                                                                                   width = 150,
                                                                                   height = 150),
                                                                        flet.Text(value = product.name,
                                                                                  color = flet.colors.BLACK,
                                                                                  weight = flet.FontWeight.W_900),
                                                                        flet.Text(value = f'x {product.in_stock}',
                                                                                  color = flet.colors.BLACK,
                                                                                  weight = flet.FontWeight.W_300),
                                                                        flet.Text(value = f'P {product.price}',
                                                                                  color = flet.colors.BLACK,
                                                                                  weight = flet.FontWeight.W_400)]))

            def set_product_cards():
                product_cards.controls = list(map(lambda l: ItemCard(product = l, click = lambda:select_product(x = l.id)), products))
                return product_cards
                
            def changeQuantity(item: CartItem):
                orgItem = None
                for each in productMatcher:
                    if item.product.id == each.id:
                        orgItem = each
                        break
                
                def checkQuantity(_):
                    if quantityField.value == "":
                        subtotalText.value = f'P 0.00'
                        return
                    elif not quantityField.value.isnumeric():
                        quantityField.value = ""
                        subtotalText.value = f'P 0.00'
                    elif int(quantityField.value) < 0:
                        quantityField.value = ""
                        subtotalText.value = f'P 0.00'
                    elif int(quantityField.value) > orgItem.in_stock:
                        quantityField.value = orgItem.in_stock
                        subtotalText.value = f'P {int(quantityField.value)*orgItem.price}'
                    else:
                        subtotalText.value = f'P {int(quantityField.value)*orgItem.price}'
                    subtotalText.update()
                    page.update()

                def on_confirm(_):
                    if quantityField.value == "":
                        return
                    elif int(quantityField.value) == 0:
                        on_remove("")
                    else:
                        for r in range(len(cartItems)):
                            if cartItems[r].product.id == item.product.id:
                                cartItems[r].quantity = int(quantityField.value)
                                cartListShow()
                                totalText.value = f'P {reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)}'
                                products[orgItem.id].in_stock = orgItem.in_stock - cartItems[r].quantity
                                set_product_cards()
                                break
                        
                        page.update()
                        on_cancel("")

                def on_cancel(_):
                    dialog.open = False
                    page.update()

                def on_remove(_):
                    def removed(_):
                        cartListView.controls.pop(cartItems.index(item))
                        cartItems.remove(item)
                        totalText.value = f'P {reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)}'
                        products[orgItem.id].in_stock = orgItem.in_stock
                        set_product_cards()
                        page.update()
                        on_cancel("")
                    dialog.title = None
                    dialog.content = flet.Container(width = 600,
                                                    height = 600,
                                                    alignment = flet.Alignment(0,0),
                                                    content = flet.Text(f'Remove {orgItem.name}(s) from Cart?'))
                    dialog.actions = [flet.TextButton('NO', on_click = None),
                                      flet.TextButton('YES',
                                                      on_click = removed)]
                    page.update()
                    

                quantityField = flet.TextField(value = f'{item.quantity}',
                                               on_change = checkQuantity)
                subtotalText = flet.Text(f'P {item.subtotal()}')

                def PROLLYNOTFORDIALOG():
                    return  flet.AlertDialog(title = flet.Text(f'{orgItem.name} [Item In Stock: {orgItem.in_stock}]'),
                                             content = flet.Container(width = 600,
                                                                      height = 600,
                                                                      content = flet.Column(alignment = flet.MainAxisAlignment.CENTER,
                                                                                            horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                                                                            controls = [flet.Image(src = orgItem.image,
                                                                                                                   width = 400,
                                                                                                                   height = 400,
                                                                                                                   fit = True),
                                                                                                        flet.Row(alignment = flet.MainAxisAlignment.CENTER,
                                                                                                                 controls = [quantityField]),
                                                                                                        subtotalText])),
                                             actions_alignment = flet.MainAxisAlignment.END,
                                             actions = [flet.TextButton('CANCEL',
                                                                        on_click = on_cancel),
                                                        flet.TextButton('REMOVE FROM CART',
                                                                        on_click = on_remove),
                                                        flet.TextButton('CONFIRM',
                                                                        on_click = on_confirm)])

                dialog = PROLLYNOTFORDIALOG()

                page.dialog = dialog
                dialog.open = True
                page.update()


            def cartListShow():
                cartListView.controls = list(map(lambda l: flet.Container(on_click = lambda _: changeQuantity(item = l),
                                                                          bgcolor = flet.colors.GREEN,
                                                                          border_radius = 5,
                                                                          padding = 20,
                                                                          margin = 2, #NAME QUANTITY PRICE SUBTOTAL
                                                                          content = flet.Row(controls = [flet.Text(value = f'{l.product.name}',
                                                                                                                   color = flet.colors.WHITE),
                                                                                                         flet.Text(value = f'x {l.quantity}',
                                                                                                                   color = flet.colors.WHITE),
                                                                                                         flet.Text(value = f'P {l.product.price}',
                                                                                                                   color = flet.colors.WHITE),
                                                                                                         flet.Text(value = f'Subtotal: P{l.subtotal()}',
                                                                                                                   color = flet.colors.WHITE)])),
                                                 cartItems))
                return cartListView
                
            def on_sale(_):
                
                def couldBeFloat(s: str):
                    dotCounter = 0
                    length = 0
                    for digit in s:
                        if dotCounter == 1:
                            length += 1
                            if length == 3:
                                return False
                        if not digit.isnumeric():
                            if dotCounter < 1 and digit == '.':
                                dotCounter += 1
                            else:
                                return False
                            
                    return True
                
                def checkChange(_):
                    if not couldBeFloat(payField.value):
                        payField.value = ""

                def on_cancel(_):
                    dialog.open = False
                    dialog.update()

                def on_main(_):
                    on_cancel("")
                    updateProductsTxt()
                    page.go('/main')

                def z(_):
                    dialog.title = flet.Image(src = 'pics/HoldUp.jpg',
                                                             width = 400,
                                                             height = 400,
                                                             fit = True)
                    dialog.content = flet.Column(alignment = flet.MainAxisAlignment.CENTER,
                                                                horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                                                controls = [flet.Text(value = f'Total: P {reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)}'),
                                                                            payField])
                    dialog.actions = [flet.TextButton('CANCEL',
                                                                     on_click = on_cancel),
                                                     flet.TextButton('CONFIRM',
                                                                     on_click = on_confirm)]
                    dialog.update()

                def on_confirm(_):
                    total = reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)
                    if payField.value == "":
                        return
                    elif float(payField.value) < total:
                        dialog.title = flet.Image(src = 'pics/gimmeMoreMoney.png',
                                                  width = 400,
                                                  height = 400,
                                                  fit = True)
                        dialog.content = flet.Text('INSUFFICIENT FUNDS',
                                                   weight = flet.FontWeight.BOLD)
                        dialog.actions = [flet.TextButton('CONTINUE',
                                                          on_click = z)]
                        dialog.update()
                    else:
                        addTransaction(float(payField.value))
                        dialog.title = flet.Image(src = 'pics/ThankYou.jpg',
                                                  width = 400,
                                                  height = 400,
                                                  fit = True)
                        dialog.content = flet.Text(f'Change: {float(payField.value) - total}',
                                                   weight = flet.FontWeight.BOLD)
                        dialog.actions = [flet.TextButton('CONTINUE',
                                                          on_click = on_main)]
                        dialog.update()

                payField = flet.TextField(label = "Ammount Paid",
                                          on_change = checkChange)
                
                def refresh_dialog():
                    return flet.AlertDialog(title = flet.Image(src = 'pics/HoldUp.jpg',
                                                             width = 400,
                                                             height = 400,
                                                             fit = True),
                                          content = flet.Column(alignment = flet.MainAxisAlignment.CENTER,
                                                                horizontal_alignment = flet.CrossAxisAlignment.CENTER,
                                                                controls = [flet.Text(value = f'Total: P {reduce(lambda a, b: a + b.subtotal(), cartItems, 0.00)}'),
                                                                            payField]),
                                          actions_alignment = flet.MainAxisAlignment.END,
                                          actions = [flet.TextButton('CANCEL',
                                                                     on_click = on_cancel),
                                                     flet.TextButton('CONFIRM',
                                                                     on_click = on_confirm)])
                dialog = refresh_dialog()
                if len(cartItems) == 0:
                    dialog.title = flet.Image(src = 'pics/TheFuckYouDoing.png',
                                              width = 400,
                                              height = 400,
                                              fit = True)
                    dialog.content = flet.Text('YOU CURRENTLY HAVE NO ITEM IN CART',
                                               weight = flet.FontWeight.BOLD)
                    dialog.actions = [flet.TextButton('CONTINUE',
                                                      on_click = on_cancel)]
                    
                page.dialog = dialog
                dialog.open = True
                page.update()

            page.views.append(flet.View(route = "/store",
                                        appbar = flet.AppBar(leading = flet.IconButton(icon = flet.icons.HOME_OUTLINED,
                                                                                       on_click = lambda _: page.go('/main')),
                                                             title = flet.Row(controls = [flet.Text(value = 'New Transaction',
                                                                                                    expand = True),
                                                                                          theme_button]),
                                                             bgcolor = flet.colors.BLUE_200),
                                        controls = [flet.ResponsiveRow(vertical_alignment = flet.CrossAxisAlignment.STRETCH,
                                                                      controls = [flet.Column(col = 9,
                                                                                              controls = [set_product_cards()]),
                                                                                  flet.Column(col = 3,
                                                                                              horizontal_alignment = flet.CrossAxisAlignment.STRETCH,
                                                                                              controls = [flet.Column(controls = [flet.Text('TOTAL '),
                                                                                                                                  totalText,
                                                                                                                                  flet.FilledButton('CHECKOUT',
                                                                                                                                                    width = 1000,
                                                                                                                                                    on_click = on_sale)]),
                                                                                                          flet.Text('---------------------------------------------------'),
                                                                                                          cartListShow()])])]))
        
        # BECAUSE APPARENTLY WE STILL NEED TO CHECK TRANSACTION HISTORY
        elif page.route == "/history":
            transactions = flet.ListView()
            transacFile = []
            def checkTransaction(order: SaleOrder):
                def on_exit(_):
                    dialog.open = False
                    dialog.update()
                dialog = flet.AlertDialog(title = flet.Text(appName,
                                                            weight = flet.FontWeight.BOLD),
                                          content = flet.Column(controls = [flet.Text(f'Cashier: {order.cashier}'),
                                                                            flet.ListView(controls = list(map(lambda l: flet.Row([flet.Text(l.product.name,
                                                                                                                                            weight = flet.FontWeight.W_700),
                                                                                                                                  flet.Text(f'x {l.quantity}',
                                                                                                                                            weight = flet.FontWeight.W_700),
                                                                                                                                  flet.Text(f'P {l.product.price}',
                                                                                                                                            weight = flet.FontWeight.W_700),
                                                                                                                                  flet.Text(f'Subtotal: P {l.subtotal()}',
                                                                                                                                            weight = flet.FontWeight.W_700)],
                                                                                                                                 alignment = flet.MainAxisAlignment.SPACE_BETWEEN),
                                                                                                              order.items))),
                                                                            flet.Row(controls = [flet.Text(f'Total: {order.total}',
                                                                                                           weight = flet.FontWeight.BOLD),
                                                                                                 flet.Text(f'Cash: {order.cash}',
                                                                                                           weight = flet.FontWeight.BOLD),
                                                                                                 flet.Text(f'Change: {order.change}',
                                                                                                           weight = flet.FontWeight.BOLD)])]),
                                          actions_alignment = flet.MainAxisAlignment.END,
                                          actions = [flet.TextButton('CONTINUE',
                                                                     on_click = on_exit)])
                page.dialog = dialog
                dialog.open = True
                page.update()

            def readTransactions():
                with open('transactions.txt') as file:
                    for line in file:
                        if "*" in line or len(line) < 5:
                            continue
                        Cashier = line[len('CASHIER:'):line.index('DATETIME:')].strip()
                        DateTime = line[(line.index('DATETIME:') + len('DATETIME:')):line.index('TOTAL:')].strip()
                        Total = float(line[(line.index('TOTAL:') + len('TOTAL:')):line.index('CASH:')].strip())
                        Cash = float(line[(line.index('CASH:') + len('CASH:')):line.index('CHANGE:')].strip())
                        Change = float(line[(line.index('CHANGE:') + len('CHANGE:')):line.index('[')].strip())
                        listLine = line[line.index('['):].strip().strip() + " "
                        Items = []
                        while listLine != " ":
                            tempString = listLine[:listLine.index(']')+1]
                            pName = tempString[len('[NAME:'):tempString.index('PRICE:')]
                            pPrice = float(listLine[(tempString.index('PRICE:') + len('PRICE:')):tempString.index('QTY:')])
                            pQty = int(listLine[(tempString.index('QTY:') + len('QTY:')): tempString.index('SUBTOTAL:')])
                            listLine = listLine[listLine.index(']')+1:]
                            Items.append(CartItem(Product(id = 999, name = pName, price = pPrice, in_stock = None, image = None), pQty))
                        transacFile.append(SaleOrder(Cashier, DateTime, Total, Cash, Change, Items))
            



                transactions.controls = list(map(lambda l: flet.Container(on_click = lambda _: checkTransaction(order = l),
                                                                          bgcolor = flet.colors.GREEN,
                                                                          border_radius = 5,
                                                                          padding = 20,
                                                                          margin = 2,
                                                                          content = flet.Row([flet.Text(f'Cashier: {l.cashier}',
                                                                                                       expand = True),
                                                                                             flet.Text(l.dt)])),
                                                 reversed(transacFile)))
                return transactions

            page.views.append(flet.View(route = "/history",
                                        appbar = flet.AppBar(leading = flet.IconButton(icon = flet.icons.HOME_OUTLINED,
                                                                                       on_click = lambda _: page.go('/main')),
                                                             title = flet.Row(controls = [flet.Text(value = 'Transaction History',
                                                                                                    expand = True),
                                                                                          theme_button]),
                                                             bgcolor = flet.colors.BLUE_200),
                                        controls = [readTransactions()]))

        page.update()

    # OUR INITIAL ROUTE BASICALLY MEANS THAT WE START AT /auth ROUTE AND THEN CHANGE ROUTES IN ACCORDANCE TO CHOSEN ACTIONS
    page.route = '/auth'
    page.on_route_change = route_change
    page.go(route = page.route)


flet.app(target = main)
