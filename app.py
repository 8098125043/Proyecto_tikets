import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import json
import os

class Ticket:
    PRIORIDADES = ["Baja", "Media", "Alta"]

    def __init__(self, id, cliente, asunto, prioridad="Media", estado="Abierto", agente_asignado=None):
        self.id = id
        self.cliente = cliente
        self.asunto = asunto
        self.prioridad = prioridad
        self.estado = estado
        self.agente_asignado = agente_asignado
        self.comentarios = []

    def __str__(self):
        return f"ID: {self.id}, Cliente: {self.cliente}, Asunto: {self.asunto}, Prioridad: {self.prioridad}, Estado: {self.estado}, Agente Asignado: {self.agente_asignado}"

class TicketManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="tickets_db"
        )
        self.cursor = self.conn.cursor()
        self.next_id = self.get_next_id()

    def get_next_id(self):
        self.cursor.execute("SELECT MAX(id) FROM tickets")
        result = self.cursor.fetchone()
        return (result[0] or 0) + 1

    def crear_ticket(self, cliente, asunto, prioridad):
        ticket = Ticket(self.next_id, cliente, asunto, prioridad)
        self.cursor.execute(
            "INSERT INTO tickets (id, cliente, asunto, prioridad, estado, agente_asignado) VALUES (%s, %s, %s, %s, %s, %s)",
            (ticket.id, ticket.cliente, ticket.asunto, ticket.prioridad, ticket.estado, ticket.agente_asignado)
        )
        self.conn.commit()
        self.next_id += 1
        return ticket

    def modificar_ticket(self, id_ticket, cliente, asunto, prioridad, estado, agente_asignado):
        self.cursor.execute(
            "UPDATE tickets SET cliente=%s, asunto=%s, prioridad=%s, estado=%s, agente_asignado=%s WHERE id=%s",
            (cliente, asunto, prioridad, estado, agente_asignado, id_ticket)
        )
        self.conn.commit()

    def eliminar_ticket(self, id_ticket):
        self.cursor.execute("DELETE FROM tickets WHERE id = %s", (id_ticket,))
        self.conn.commit()

    def listar_tickets(self):
        self.cursor.execute("SELECT * FROM tickets")
        tickets = self.cursor.fetchall()
        tickets_info = []
        for ticket in tickets:
            ticket_info = f"ID: {ticket[0]}, Cliente: {ticket[1]}, Asunto: {ticket[2]}, Prioridad: {ticket[3]}, Estado: {ticket[4]}, Agente Asignado: {ticket[5]}"
            tickets_info.append(ticket_info)
        return tickets_info

    def buscar_tickets_por_cliente(self, cliente):
        self.cursor.execute("SELECT * FROM tickets WHERE cliente = %s", (cliente,))
        return self.cursor.fetchall()

    def buscar_tickets_por_estado(self, estado):
        self.cursor.execute("SELECT * FROM tickets WHERE estado = %s", (estado,))
        return self.cursor.fetchall()

    def asignar_agente(self, id_ticket, agente):
        self.cursor.execute("UPDATE tickets SET agente_asignado = %s WHERE id = %s", (agente, id_ticket))
        self.conn.commit()

    def cerrar_ticket(self, id_ticket):
        self.cursor.execute("UPDATE tickets SET estado = 'Cerrado' WHERE id = %s", (id_ticket,))
        self.conn.commit()

    def buscar_ticket_por_id(self, id_ticket):
        self.cursor.execute("SELECT * FROM tickets WHERE id = %s", (id_ticket,))
        return self.cursor.fetchone()

    def exportar_tickets_json(self, nombre_archivo, ruta):
        ruta_completa = os.path.join(ruta, nombre_archivo)
        self.cursor.execute("SELECT * FROM tickets")
        tickets = self.cursor.fetchall()
        tickets_data = []
        for ticket in tickets:
            ticket_data = {
                "ID": ticket[0],
                "Cliente": ticket[1],
                "Asunto": ticket[2],
                "Prioridad": ticket[3],
                "Estado": ticket[4],
                "Agente Asignado": ticket[5]
            }
            tickets_data.append(ticket_data)

        with open(ruta_completa, 'w') as file:
            json.dump(tickets_data, file, indent=4)

class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Tickets")
        self.ticket_manager = TicketManager()

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_ticket_frame = self.create_ticket_tab()
        self.modify_ticket_frame = self.modify_ticket_tab()
        self.delete_ticket_frame = self.delete_ticket_tab()
        self.list_tickets_frame = self.list_tickets_tab()
        self.assign_agent_frame = self.assign_agent_tab()
        self.close_ticket_frame = self.close_ticket_tab()
        self.search_client_frame = self.search_client_tab()
        self.search_state_frame = self.search_state_tab()
        self.export_frame = self.export_tab()

    def create_ticket_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Crear Ticket")

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, padx=10, pady=10)
        self.cliente_entry = ttk.Entry(frame, width=50)
        self.cliente_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Asunto:").grid(row=1, column=0, padx=10, pady=10)
        self.asunto_entry = ttk.Entry(frame, width=50)
        self.asunto_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Prioridad:").grid(row=2, column=0, padx=10, pady=10)
        self.prioridad_combobox = ttk.Combobox(frame, values=Ticket.PRIORIDADES, state="readonly")
        self.prioridad_combobox.set("Media")
        self.prioridad_combobox.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Crear Ticket", command=self.crear_ticket).grid(row=3, column=0, columnspan=2, pady=10)

        return frame

    def modify_ticket_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Modificar Ticket")

        ttk.Label(frame, text="ID del Ticket:").grid(row=0, column=0, padx=10, pady=10)
        self.modify_id_entry = ttk.Entry(frame, width=50)
        self.modify_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Cliente:").grid(row=1, column=0, padx=10, pady=10)
        self.modify_cliente_entry = ttk.Entry(frame, width=50)
        self.modify_cliente_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Asunto:").grid(row=2, column=0, padx=10, pady=10)
        self.modify_asunto_entry = ttk.Entry(frame, width=50)
        self.modify_asunto_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Prioridad:").grid(row=3, column=0, padx=10, pady=10)
        self.modify_prioridad_combobox = ttk.Combobox(frame, values=Ticket.PRIORIDADES, state="readonly")
        self.modify_prioridad_combobox.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Estado:").grid(row=4, column=0, padx=10, pady=10)
        self.modify_estado_combobox = ttk.Combobox(frame, values=["Abierto", "Cerrado"], state="readonly")
        self.modify_estado_combobox.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Agente Asignado:").grid(row=5, column=0, padx=10, pady=10)
        self.modify_agente_entry = ttk.Entry(frame, width=50)
        self.modify_agente_entry.grid(row=5, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Modificar Ticket", command=self.modificar_ticket).grid(row=6, column=0, columnspan=2, pady=10)

        return frame

    def delete_ticket_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Eliminar Ticket")

        ttk.Label(frame, text="ID del Ticket:").grid(row=0, column=0, padx=10, pady=10)
        self.delete_id_entry = ttk.Entry(frame, width=50)
        self.delete_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Eliminar Ticket", command=self.eliminar_ticket).grid(row=1, column=0, columnspan=2, pady=10)

        return frame

    def list_tickets_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Listar Tickets")

        self.list_tickets_text = tk.Text(frame, width=80, height=20)
        self.list_tickets_text.grid(row=0, column=0, padx=10, pady=10)

        ttk.Button(frame, text="Actualizar Lista", command=self.actualizar_lista).grid(row=1, column=0, padx=10, pady=10)

        return frame

    def assign_agent_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Asignar Agente")

        ttk.Label(frame, text="ID del Ticket:").grid(row=0, column=0, padx=10, pady=10)
        self.assign_id_entry = ttk.Entry(frame, width=50)
        self.assign_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Agente Asignado:").grid(row=1, column=0, padx=10, pady=10)
        self.assign_agent_entry = ttk.Entry(frame, width=50)
        self.assign_agent_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Asignar Agente", command=self.asignar_agente).grid(row=2, column=0, columnspan=2, pady=10)

        return frame

    def close_ticket_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Cerrar Ticket")

        ttk.Label(frame, text="ID del Ticket:").grid(row=0, column=0, padx=10, pady=10)
        self.close_id_entry = ttk.Entry(frame, width=50)
        self.close_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Cerrar Ticket", command=self.cerrar_ticket).grid(row=1, column=0, columnspan=2, pady=10)

        return frame

    def search_client_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Buscar por Cliente")

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, padx=10, pady=10)
        self.search_client_entry = ttk.Entry(frame, width=50)
        self.search_client_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Buscar", command=self.buscar_por_cliente).grid(row=1, column=0, columnspan=2, pady=10)

        return frame

    def search_state_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Buscar por Estado")

        ttk.Label(frame, text="Estado:").grid(row=0, column=0, padx=10, pady=10)
        self.search_state_combobox = ttk.Combobox(frame, values=["Abierto", "Cerrado"], state="readonly")
        self.search_state_combobox.grid(row=0, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Buscar", command=self.buscar_por_estado).grid(row=1, column=0, columnspan=2, pady=10)

        return frame

    def export_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Exportar Tickets")

        ttk.Label(frame, text="Nombre del Archivo:").grid(row=0, column=0, padx=10, pady=10)
        self.export_filename_entry = ttk.Entry(frame, width=50)
        self.export_filename_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Ruta de Exportación:").grid(row=1, column=0, padx=10, pady=10)
        self.export_path_entry = ttk.Entry(frame, width=50)
        self.export_path_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(frame, text="Exportar a JSON", command=self.exportar_tickets_json).grid(row=2, column=0, columnspan=2, pady=10)

        return frame

    def crear_ticket(self):
        cliente = self.cliente_entry.get()
        asunto = self.asunto_entry.get()
        prioridad = self.prioridad_combobox.get()

        if cliente and asunto:
            ticket = self.ticket_manager.crear_ticket(cliente, asunto, prioridad)
            messagebox.showinfo("Éxito", f"Se ha creado el ticket con ID: {ticket.id}")
            self.cliente_entry.delete(0, tk.END)
            self.asunto_entry.delete(0, tk.END)
            self.prioridad_combobox.set("Media")
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")

    def modificar_ticket(self):
        id_ticket = self.modify_id_entry.get()
        cliente = self.modify_cliente_entry.get()
        asunto = self.modify_asunto_entry.get()
        prioridad = self.modify_prioridad_combobox.get()
        estado = self.modify_estado_combobox.get()
        agente = self.modify_agente_entry.get()

        if id_ticket and cliente and asunto:
            self.ticket_manager.modificar_ticket(id_ticket, cliente, asunto, prioridad, estado, agente)
            messagebox.showinfo("Éxito", f"Se ha modificado el ticket con ID: {id_ticket}")
            self.modify_id_entry.delete(0, tk.END)
            self.modify_cliente_entry.delete(0, tk.END)
            self.modify_asunto_entry.delete(0, tk.END)
            self.modify_prioridad_combobox.set("")
            self.modify_estado_combobox.set("")
            self.modify_agente_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")

    def eliminar_ticket(self):
        id_ticket = self.delete_id_entry.get()
        if id_ticket:
            confirmacion = messagebox.askyesno("Confirmación", f"¿Estás seguro de eliminar el ticket con ID: {id_ticket}?")
            if confirmacion:
                self.ticket_manager.eliminar_ticket(id_ticket)
                messagebox.showinfo("Éxito", f"Se ha eliminado el ticket con ID: {id_ticket}")
                self.delete_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Por favor, introduce el ID del ticket a eliminar.")

    def actualizar_lista(self):
        tickets = self.ticket_manager.listar_tickets()
        self.list_tickets_text.delete(1.0, tk.END)
        for ticket in tickets:
            self.list_tickets_text.insert(tk.END, str(ticket) + "\n")

    def asignar_agente(self):
        id_ticket = self.assign_id_entry.get()
        agente = self.assign_agent_entry.get()

        if id_ticket and agente:
            self.ticket_manager.asignar_agente(id_ticket, agente)
            messagebox.showinfo("Éxito", f"Se ha asignado el agente {agente} al ticket con ID: {id_ticket}")
            self.assign_id_entry.delete(0, tk.END)
            self.assign_agent_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")

    def cerrar_ticket(self):
        id_ticket = self.close_id_entry.get()
        if id_ticket:
            confirmacion = messagebox.askyesno("Confirmación", f"¿Estás seguro de cerrar el ticket con ID: {id_ticket}?")
            if confirmacion:
                self.ticket_manager.cerrar_ticket(id_ticket)
                messagebox.showinfo("Éxito", f"Se ha cerrado el ticket con ID: {id_ticket}")
                self.close_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Por favor, introduce el ID del ticket a cerrar.")

    def buscar_por_cliente(self):
        cliente = self.search_client_entry.get()
        if cliente:
            tickets = self.ticket_manager.buscar_tickets_por_cliente(cliente)
            self.list_tickets_text.delete(1.0, tk.END)
            for ticket in tickets:
                self.list_tickets_text.insert(tk.END, str(ticket) + "\n")
        else:
            messagebox.showerror("Error", "Por favor, introduce el nombre del cliente.")

    def buscar_por_estado(self):
        estado = self.search_state_combobox.get()
        if estado:
            tickets = self.ticket_manager.buscar_tickets_por_estado(estado)
            self.list_tickets_text.delete(1.0, tk.END)
            for ticket in tickets:
                self.list_tickets_text.insert(tk.END, str(ticket) + "\n")
        else:
            messagebox.showerror("Error", "Por favor, selecciona un estado.")

    def exportar_tickets_json(self):
        nombre_archivo = self.export_filename_entry.get()
        ruta = self.export_path_entry.get()

        if nombre_archivo and ruta:
            self.ticket_manager.exportar_tickets_json(nombre_archivo, ruta)
            messagebox.showinfo("Éxito", f"Se han exportado los tickets como '{nombre_archivo}' en la ruta '{ruta}'.")
            self.export_filename_entry.delete(0, tk.END)
            self.export_path_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Por favor, completa todos los campos.")

root = tk.Tk()
app = TicketApp(root)
root.mainloop()
