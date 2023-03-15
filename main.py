import mysql.connector
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Minecraft01@",
  database="boutique"
)

mycursor = mydb.cursor()


class Category:
    def __init__(self, id, nom):
        self.id = id
        self.nom = nom


class Product:
    def __init__(self, id, nom, description, prix, quantite, categorie):
        self.id = id
        self.nom = nom
        self.description = description
        self.prix = prix
        self.quantite = quantite
        self.categorie = categorie


class Application:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestion de stock")
        self.master.geometry("1440x600")

        # Create a treeview to display the products
        self.tree = ttk.Treeview(self.master)
        self.tree["columns"] = ("id", "nom", "description", "prix", "quantite", "categorie")
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("description", text="Description")
        self.tree.heading("prix", text="Prix")
        self.tree.heading("quantite", text="Quantité")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.pack()

        # Add buttons to add, delete, and edit products
        product_buttons_frame = tk.LabelFrame(self.master, text="Produit", padx=5, pady=5)
        product_buttons_frame.pack(side="left", padx=10, pady=10, fill="y", expand=True)
        add_button = tk.Button(product_buttons_frame, text="Ajouter", command=self.add_product)
        add_button.pack(expand=True)
        delete_button = tk.Button(product_buttons_frame, text="Supprimer", command=self.delete_product)
        delete_button.pack(expand=True)
        edit_button = tk.Button(product_buttons_frame, text="Modifier", command=self.edit_product)
        edit_button.pack(expand=True)

        category_buttons_frame = tk.LabelFrame(self.master, text="Catégorie", padx=5, pady=5)
        category_buttons_frame.pack(side="left",padx=10, pady=10, fill="y", expand=True)

        delete_cat_button = tk.Button(category_buttons_frame, text="Supprimer catégorie", command=self.delete_category)
        delete_cat_button.pack()

        export_button_frame = tk.LabelFrame(self.master, text="Exporter", padx=5, pady=5)
        export_button_frame.pack(side="left", padx=10, pady=10, fill="y", expand=True)


        export_to_csv_button = tk.Button(export_button_frame, text="Exporter vers CSV", command=lambda : self.export_csv("produit.csv"))
        export_to_csv_button.pack()

        # Load the products from the database
        self.load_products()

    def load_products(self):
        # Clear the treeview
        quantity_dict = {}
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Fetch the products from the database
        mycursor.execute("SELECT * FROM produit")
        rows = mycursor.fetchall()

        # Populate the treeview with the products
        for row in rows:
            categorie = self.get_categorie_by_id(row[5])
            product = Product(row[0], row[1], row[2], row[3], row[4], categorie)
            try:
                self.tree.insert("", "end", values=(
                product.id, product.nom, product.description, product.prix, product.quantite, product.categorie.nom))
            except:
                self.tree.insert("", "end", values=(
                product.id, product.nom, product.description, product.prix, product.quantite, "None"))

    def add_product(self):
        # Create a new window to add a product
        add_window = tk.Toplevel(self.master)
        add_window.title("Ajouter un produit")

        # Add labels and entry widgets for the product details
        nom_label = tk.Label(add_window, text="Nom:")
        nom_label.pack()
        nom_entry = tk.Entry(add_window)
        nom_entry.pack()

        description_label = tk.Label(add_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(add_window)
        description_entry.pack()

        prix_label = tk.Label(add_window, text="Prix:")
        prix_label.pack()
        prix_entry = tk.Entry(add_window)
        prix_entry.pack()

        quantite_label = tk.Label(add_window, text="Quantité:")
        quantite_label.pack()
        quantite_entry = tk.Entry(add_window)
        quantite_entry.pack()

        categorie_label = tk.Label(add_window, text="Catégorie:")
        categorie_label.pack()
        categorie_box = ttk.Combobox(add_window, values=self.get_categories())
        categorie_box.pack()

        # Add a button to save the new product
        save_button = tk.Button(add_window, text="Enregistrer",
                                command=lambda: self.save_product(nom_entry.get(), description_entry.get(),
                                                                  prix_entry.get(), quantite_entry.get(),
                                                                  categorie_box.get(), add_window))
        save_button.pack()

    def save_product(self, nom, description, prix, quantite, categorie_nom, window):
        # Check if the category already exists, otherwise create a new one
        categorie = self.get_categorie_by_nom(categorie_nom)
        print(categorie)
        if categorie is None:
            mycursor.execute("INSERT INTO categorie (nom) VALUES (%s)", (categorie_nom,))
            mydb.commit()
            categorie_id = mycursor.lastrowid
            categorie = Category(categorie_id, categorie_nom)

        # Insert the new product into the database
        mycursor.execute(
            "INSERT INTO produit (nom, description, prix, quantite, id_categorie) VALUES (%s, %s, %s, %s, %s)",
            (nom, description, prix, quantite, categorie.id))
        mydb.commit()

        # Close the add window and reload the products
        messagebox.showinfo("Succès", "Le produit a été ajouté avec succès.")
        self.load_products()
        window.destroy()

    def delete_product(self):
        # Get the selected product
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]
        product_id = values[0]

        # Ask for confirmation
        confirmation = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce produit?")
        if not confirmation:
            return
        # Delete the product from the database
        mycursor.execute("DELETE FROM produit WHERE id = %s", (product_id,))
        mydb.commit()

        # Reload the products
        self.load_products()

    def edit_product(self):
        # Get the selected product
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)["values"]
        product_id = values[0]

        # Get the existing product details from the database
        mycursor.execute("SELECT * FROM produit WHERE id = %s", (product_id,))
        row = mycursor.fetchone()
        categorie = self.get_categorie_by_id(row[5])
        product = Product(row[0], row[1], row[2], row[3], row[4], categorie)

        # Create a new window to edit the product
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Modifier le produit")

        # Add labels and entry widgets for the product details
        nom_label = tk.Label(edit_window, text="Nom:")
        nom_label.pack()
        nom_entry = tk.Entry(edit_window)
        nom_entry.insert(0, product.nom)
        nom_entry.pack()

        description_label = tk.Label(edit_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(edit_window)
        description_entry.insert(0, product.description)
        description_entry.pack()

        prix_label = tk.Label(edit_window, text="Prix:")
        prix_label.pack()
        prix_entry = tk.Entry(edit_window)
        prix_entry.insert(0, product.prix)
        prix_entry.pack()

        quantite_label = tk.Label(edit_window, text="Quantité:")
        quantite_label.pack()
        quantite_entry = tk.Entry(edit_window)
        quantite_entry.insert(0, product.quantite)
        quantite_entry.pack()

        categorie_label = tk.Label(edit_window, text="Catégorie:")
        categorie_label.pack()
        categorie_box = ttk.Combobox(edit_window, values=self.get_categories())
        categorie_box.pack()

        # Add a button to save the edited product
        save_button = tk.Button(edit_window, text="Enregistrer",
                                command=lambda: self.save_edited_product(product_id, nom_entry.get(),
                                                                         description_entry.get(), prix_entry.get(),
                                                                         quantite_entry.get(), categorie_box.get(), edit_window))
        save_button.pack()

    def save_edited_product(self, product_id, nom, description, prix, quantite, categorie_nom, window):
        # Check if the category already exists, otherwise create a new one
        categorie = self.get_categorie_by_nom(categorie_nom)
        if categorie is None:
            mycursor.execute("INSERT INTO categorie (nom) VALUES (%s)", (categorie_nom,))
            mydb.commit()
            categorie_id = mycursor.lastrowid
            categorie = Category(categorie_id, categorie_nom)

        # Update the product in the database
        mycursor.execute(
            "UPDATE produit SET nom = %s, description = %s, prix = %s, quantite = %s, id_categorie = %s WHERE id = %s",
            (nom, description, prix, quantite, categorie.id, product_id))
        mydb.commit()

        # Close the edit window and reload the products
        messagebox.showinfo("Succès", "Le produit a été modifié avec succès.")
        self.load_products()
        window.destroy()

    def get_categorie_by_id(self, categorie_id):
        # Fetch a category from the database by ID
        try:
            mycursor.execute("SELECT * FROM categorie WHERE id = %s", (categorie_id,))
            row = mycursor.fetchone()
            if row is not None:
                return Category(row[0], row[1])
            else:
                return None
        except:
            return "None"

    def get_categorie_by_nom(self, categorie_nom):
        # Fetch a category from the database by name
        try:
            mycursor.execute("SELECT * FROM categorie WHERE nom = %s", (categorie_nom,))
            row = mycursor.fetchone()
            if row is not None:
                return Category(row[0], row[1])
            else:
                return None
        except:
            return "None"

    def load_categories(self):
        # Clear the categories treeview
        self.tree_categories.delete(*self.tree_categories.get_children())

        # Fetch the categories from the database
        mycursor.execute("SELECT * FROM categorie")
        rows = mycursor.fetchall()

        # Insert the categories into the treeview
        for row in rows:
            self.tree_categories.insert("", tk.END, values=row)

    def add_category(self):
        # Create a new window to add a category
        add_window = tk.Toplevel(self.master)
        add_window.title("Ajouter une catégorie")

        # Add a label and entry widget for the category name
        nom_label = tk.Label(add_window, text="Nom:")
        nom_label.pack()
        nom_entry = tk.Entry(add_window)
        nom_entry.pack()

        # Add a button to save the new category
        save_button = tk.Button(add_window, text="Enregistrer",
                                command=lambda: self.save_category(nom_entry.get(), add_window))
        save_button.pack()

    def save_category(self, nom , window):
        # Insert the new category into the database
        mycursor.execute("INSERT INTO categorie (nom) VALUES (%s)", (nom,))
        mydb.commit()

        # Close the add window and reload the categories
        messagebox.showinfo("Succès", "La catégorie a été ajoutée avec succès.")
        self.load_categories()
        window.destroy()

    def delete_category(self):
        remove_window = tk.Toplevel(self.master)
        remove_window.title("Supprimer une catégorie")

        # Add a label and entry widget for the category name
        nom_label = tk.Label(remove_window, text="Nom:")
        nom_label.pack()

        nom_box = ttk.Combobox(remove_window, values=self.get_categories())
        nom_box.pack()

        save_button = tk.Button(remove_window, text="Supprimer",
                                command=lambda: self.remove_category(nom_box.get(), remove_window))
        save_button.pack()
        self.load_categories()

    def remove_category(self, nom, window):
        mycursor.execute("DELETE FROM categorie WHERE nom = %s", (nom,))
        mydb.commit()
        messagebox.showinfo("Succès", "La catégorie a été supprimée avec succès.")
        self.load_categories()
        window.destroy()

    def get_categories(self):
        mycursor.execute("SELECT nom FROM categorie")
        rows = mycursor.fetchall()
        return rows

    def get_all_products(self):
        mycursor.execute("SELECT * FROM produit")
        rows = mycursor.fetchall()
        return rows

    def export_csv(self,filename):

        # Fetch the data from the database
        data = mycursor.fetchall()

        # Write the data to a CSV file
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row
            writer.writerow([i[0] for i in mycursor.description])
            # Write the data rows
            for row in data:
                writer.writerow(row)
        messagebox.showinfo("Succès", "Les données ont été exportées avec succès.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestion de stock")
    app = Application(root)
    root.mainloop()
