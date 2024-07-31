import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class Wrestler:
    def __init__(self, name="", sex="Male", height="", weight="", hometown="", tv_grade="C", grudge_grade=0, skills={}, specialty={}, finisher={}, image="placeholder.png"):
        self.name = name
        self.sex = sex
        self.height = height
        self.weight = weight
        self.hometown = hometown
        self.tv_grade = tv_grade
        self.grudge_grade = grudge_grade
        self.skills = skills
        self.specialty = specialty or {"name": "", "points": ""}
        self.finisher = finisher or {"name": "", "range": ""}
        self.image = image

class WrestlerEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Wrestler Editor")
        self.master.geometry("1200x600")
        self.wrestlers = self.load_wrestlers()
        self.current_wrestler = None        
        self.setup_ui()

    def add_skill(self):
        skill = self.skill_var.get()
        skill_type = self.skill_type_var.get()
        if skill and skill_type:
            self.current_wrestler.skills[skill] = skill_type.lower()
            self.skills_listbox.insert(tk.END, f"{skill}: {skill_type.capitalize()}")

    def clear_form(self):
        self.name_var.set("")
        self.sex_var.set("Male")
        self.height_var.set("")
        self.weight_var.set("")
        self.hometown_var.set("")
        self.tv_grade_var.set("C")
        self.grudge_grade_var.set("0")
        self.specialty_name_var.set("")
        self.specialty_points_var.set("")
        self.finisher_name_var.set("")
        self.finisher_range_var.set("")
        self.skills_listbox.delete(0, tk.END)

    def delete_wrestler(self):
        selection = self.wrestler_listbox.curselection()
        if selection:
            index = selection[0]
            del self.wrestlers[index]
            self.update_wrestler_list()
            self.current_wrestler = None
            self.load_wrestler_details()

    def load_wrestler_details(self):
        if self.current_wrestler:
            self.name_var.set(self.current_wrestler.name)
            self.sex_var.set(self.current_wrestler.sex)
            self.height_var.set(self.current_wrestler.height)
            self.weight_var.set(self.current_wrestler.weight)
            self.hometown_var.set(self.current_wrestler.hometown)
            self.tv_grade_var.set(self.current_wrestler.tv_grade)
            self.grudge_grade_var.set(str(self.current_wrestler.grudge_grade))
            self.specialty_name_var.set(self.current_wrestler.specialty["name"])
            self.specialty_points_var.set(self.current_wrestler.specialty["points"])
            self.finisher_name_var.set(self.current_wrestler.finisher["name"])
            self.finisher_range_var.set(self.current_wrestler.finisher["range"])
            
            self.skills_listbox.delete(0, tk.END)
            for skill, skill_type in self.current_wrestler.skills.items():
                self.skills_listbox.insert(tk.END, f"{skill}: {skill_type.capitalize()}")

    def load_wrestlers(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return [Wrestler(**w) for w in data['wrestlers']]
        except FileNotFoundError:
            return []

    def new_wrestler(self):
        self.current_wrestler = Wrestler()
        self.wrestlers.append(self.current_wrestler)
        self.update_wrestler_list()
        self.clear_form()
        self.load_wrestler_details()

    def on_select(self, event):
        selection = self.wrestler_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_wrestler = self.wrestlers[index]
            self.load_wrestler_details()

    def remove_skill(self):
        selection = self.skills_listbox.curselection()
        if selection:
            index = selection[0]
            skill = self.skills_listbox.get(index).split(":")[0].strip()
            del self.current_wrestler.skills[skill]
            self.skills_listbox.delete(index)

    def save_current_wrestler(self):
        if self.current_wrestler:
            self.current_wrestler.name = self.name_var.get()
            self.current_wrestler.sex = self.sex_var.get()
            self.current_wrestler.height = self.height_var.get()
            self.current_wrestler.weight = self.weight_var.get()
            self.current_wrestler.hometown = self.hometown_var.get()
            self.current_wrestler.tv_grade = self.tv_grade_var.get()
            self.current_wrestler.grudge_grade = int(self.grudge_grade_var.get())
            self.current_wrestler.specialty["name"] = self.specialty_name_var.get()
            self.current_wrestler.specialty["points"] = self.specialty_points_var.get()
            self.current_wrestler.specialty["type"] = "STAR"
            self.current_wrestler.finisher["name"] = self.finisher_name_var.get()
            self.current_wrestler.finisher["range"] = self.finisher_range_var.get()
            self.update_wrestler_list()
            messagebox.showinfo("Success", "Wrestler saved successfully!")
        else:
            messagebox.showwarning("Warning", "No wrestler selected to save.")

    def save_wrestlers(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = {'wrestlers': [vars(w) for w in self.wrestlers]}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Success", "All wrestlers saved successfully!")

    def setup_ui(self):
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Left frame for wrestler list
        left_frame = ttk.Frame(self.master, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")

        self.wrestler_listbox = tk.Listbox(left_frame, width=30)
        self.wrestler_listbox.pack(expand=True, fill="both")
        self.wrestler_listbox.bind('<<ListboxSelect>>', self.on_select)
        self.update_wrestler_list()

        ttk.Button(left_frame, text="New Wrestler", command=self.new_wrestler).pack(pady=5)
        ttk.Button(left_frame, text="Delete Wrestler", command=self.delete_wrestler).pack(pady=5)
        ttk.Button(left_frame, text="Save All Wrestlers", command=self.save_wrestlers).pack(pady=5)

        # Middle frame for personal details and wrestling stats
        middle_frame = ttk.Frame(self.master, padding="10")
        middle_frame.grid(row=0, column=1, sticky="nsew")
        middle_frame.columnconfigure(1, weight=1)

        # Personal Details
        ttk.Label(middle_frame, text="Personal Details", font=("", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.name_var = tk.StringVar()
        self.sex_var = tk.StringVar(value="Male")
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.hometown_var = tk.StringVar()

        ttk.Label(middle_frame, text="Name:").grid(row=1, column=0, sticky="e", pady=2)
        ttk.Entry(middle_frame, textvariable=self.name_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(middle_frame, text="Sex:").grid(row=2, column=0, sticky="e", pady=2)
        ttk.Combobox(middle_frame, textvariable=self.sex_var, values=["Male", "Female"]).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(middle_frame, text="Height:").grid(row=3, column=0, sticky="e", pady=2)
        ttk.Entry(middle_frame, textvariable=self.height_var).grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(middle_frame, text="Weight:").grid(row=4, column=0, sticky="e", pady=2)
        ttk.Entry(middle_frame, textvariable=self.weight_var).grid(row=4, column=1, sticky="ew", pady=2)

        ttk.Label(middle_frame, text="Hometown:").grid(row=5, column=0, sticky="e", pady=2)
        ttk.Entry(middle_frame, textvariable=self.hometown_var).grid(row=5, column=1, sticky="ew", pady=2)

        # Wrestling Stats
        ttk.Label(middle_frame, text="Wrestling Stats", font=("", 12, "bold")).grid(row=6, column=0, columnspan=2, pady=10)

        self.tv_grade_var = tk.StringVar(value="C")
        self.grudge_grade_var = tk.StringVar(value="0")

        ttk.Label(middle_frame, text="TV Grade:").grid(row=7, column=0, sticky="e", pady=2)
        ttk.Combobox(middle_frame, textvariable=self.tv_grade_var, values=["AAA", "AA", "A", "B", "C", "D", "E", "F"]).grid(row=7, column=1, sticky="ew", pady=2)

        ttk.Label(middle_frame, text="Grudge Grade:").grid(row=8, column=0, sticky="e", pady=2)
        ttk.Entry(middle_frame, textvariable=self.grudge_grade_var).grid(row=8, column=1, sticky="ew", pady=2)

        # Right frame for skills, specialty, and finisher
        right_frame = ttk.Frame(self.master, padding="10")
        right_frame.grid(row=0, column=2, sticky="nsew")
        right_frame.columnconfigure(1, weight=1)

        # Skills
        ttk.Label(right_frame, text="Skills", font=("", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.skills = sorted(["Agile", "Cheat", "Favorite", "Grudge", "Heavy", "Helped", "Mean", "Object", "Powerful", "Quick", "Smart", "Strong"])
        self.skill_var = tk.StringVar()
        self.skill_type_var = tk.StringVar()

        ttk.Label(right_frame, text="Skill:").grid(row=1, column=0, sticky="e", pady=2)
        ttk.Combobox(right_frame, textvariable=self.skill_var, values=self.skills).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(right_frame, text="Type:").grid(row=2, column=0, sticky="e", pady=2)
        ttk.Combobox(right_frame, textvariable=self.skill_type_var, values=["Star", "Circle", "Square"]).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Button(right_frame, text="Add Skill", command=self.add_skill).grid(row=3, column=0, columnspan=2, pady=5)

        self.skills_listbox = tk.Listbox(right_frame, height=5)
        self.skills_listbox.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Button(right_frame, text="Remove Skill", command=self.remove_skill).grid(row=5, column=0, columnspan=2, pady=5)

        # Specialty
        ttk.Label(right_frame, text="Specialty", font=("", 12, "bold")).grid(row=6, column=0, columnspan=2, pady=10)

        self.specialty_name_var = tk.StringVar()
        self.specialty_points_var = tk.StringVar()

        ttk.Label(right_frame, text="Name:").grid(row=7, column=0, sticky="e", pady=2)
        ttk.Entry(right_frame, textvariable=self.specialty_name_var).grid(row=7, column=1, sticky="ew", pady=2)

        ttk.Label(right_frame, text="Points:").grid(row=8, column=0, sticky="e", pady=2)
        ttk.Entry(right_frame, textvariable=self.specialty_points_var).grid(row=8, column=1, sticky="ew", pady=2)

        # Finisher
        ttk.Label(right_frame, text="Finisher", font=("", 12, "bold")).grid(row=9, column=0, columnspan=2, pady=10)

        self.finisher_name_var = tk.StringVar()
        self.finisher_range_var = tk.StringVar()

        ttk.Label(right_frame, text="Name:").grid(row=10, column=0, sticky="e", pady=2)
        ttk.Entry(right_frame, textvariable=self.finisher_name_var).grid(row=10, column=1, sticky="ew", pady=2)

        ttk.Label(right_frame, text="Range:").grid(row=11, column=0, sticky="e", pady=2)
        ttk.Entry(right_frame, textvariable=self.finisher_range_var).grid(row=11, column=1, sticky="ew", pady=2)

        ttk.Button(right_frame, text="Save Current Wrestler", command=self.save_current_wrestler).grid(row=12, column=0, columnspan=2, pady=10)

    def update_wrestler_list(self):
        self.wrestler_listbox.delete(0, tk.END)
        for wrestler in self.wrestlers:
            self.wrestler_listbox.insert(tk.END, wrestler.name)

def main():
    root = tk.Tk()
    WrestlerEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()