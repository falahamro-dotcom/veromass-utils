import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import pandas as pd
import uuid
from datetime import datetime
from supabase import create_client

SUPABASE_URL = "https://ufnyuccqnbdkwdroyggo.supabase.co"

COLUMN_MAP = {
    "Batch_ID":                   "chrom_id",
    "Compound_ID":                "compound_id",
    "Name":                       "name",
    "Formula":                    "formula",
    "MolWt":                      "molwt",
    "POS_Matched":                "pos_matched",
    "POS_Adduct":                 "pos_adduct",
    "POS_mz":                     "pos_mz",
    "POS_Delta_mDa":              "pos_delta_mda",
    "POS_RT_min":                 "pos_rt",
    "POS_Intensity":              "pos_intensity",
    "POS_Fragments":              "pos_frags",
    "NEG_Matched":                "neg_matched",
    "NEG_Adduct":                 "neg_adduct",
    "NEG_mz":                     "neg_mz",
    "NEG_Delta_mDa":              "neg_delta_mda",
    "NEG_RT_min":                 "neg_rt",
    "NEG_Intensity":              "neg_intensity",
    "NEG_Fragments":              "neg_frags",
    "POS_[M+H]+_mz":             "pos_h_mz",
    "POS_[M+H]+_Delta_mDa":      "pos_h_delta_mda",
    "POS_[M+H]+_RT":             "pos_h_rt",
    "POS_[M+H]+_Int":            "pos_h_intensity",
    "POS_[M+NH4]+_mz":           "pos_nh4_mz",
    "POS_[M+NH4]+_Delta_mDa":    "pos_nh4_delta_mda",
    "POS_[M+NH4]+_RT":           "pos_nh4_rt",
    "POS_[M+NH4]+_Int":          "pos_nh4_intensity",
    "POS_[M+Na]+_mz":            "pos_na_mz",
    "POS_[M+Na]+_Delta_mDa":     "pos_na_delta_mda",
    "POS_[M+Na]+_RT":            "pos_na_rt",
    "POS_[M+Na]+_Int":           "pos_na_intensity",
    "POS_[M+K]+_mz":             "pos_k_mz",
    "POS_[M+K]+_Delta_mDa":      "pos_k_delta_mda",
    "POS_[M+K]+_RT":             "pos_k_rt",
    "POS_[M+K]+_Int":            "pos_k_intensity",
    "NEG_[M-H]-_mz":             "neg_mh_mz",
    "NEG_[M-H]-_Delta_mDa":      "neg_mh_delta_mda",
    "NEG_[M-H]-_RT":             "neg_mh_rt",
    "NEG_[M-H]-_Int":            "neg_mh_intensity",
    "NEG_[M+Cl]-_mz":            "neg_cl_mz",
    "NEG_[M+Cl]-_Delta_mDa":     "neg_cl_delta_mda",
    "NEG_[M+Cl]-_RT":            "neg_cl_rt",
    "NEG_[M+Cl]-_Int":           "neg_cl_intensity",
    "NEG_[M+HCOO]-_mz":          "neg_hcoo_mz",
    "NEG_[M+HCOO]-_Delta_mDa":   "neg_hcoo_delta_mda",
    "NEG_[M+HCOO]-_RT":          "neg_hcoo_rt",
    "NEG_[M+HCOO]-_Int":         "neg_hcoo_intensity",
    "NEG_[M+CH3COO]-_mz":        "neg_ch3coo_mz",
    "NEG_[M+CH3COO]-_Delta_mDa": "neg_ch3coo_delta_mda",
    "NEG_[M+CH3COO]-_RT":        "neg_ch3coo_rt",
    "NEG_[M+CH3COO]-_Int":       "neg_ch3coo_intensity",
}


class ImportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VeroMass — Import Compounds")
        self.root.geometry("560x380")
        self.root.resizable(False, False)

        pad = {"padx": 16, "pady": 6}

        # API Key
        tk.Label(root, text="Supabase Service Role Key:", anchor="w").pack(fill="x", **pad)
        self.key_var = tk.StringVar()
        tk.Entry(root, textvariable=self.key_var, show="*", width=60).pack(fill="x", **pad)

        # File picker
        tk.Label(root, text="Excel File (.xlsx):", anchor="w").pack(fill="x", **pad)
        file_frame = tk.Frame(root)
        file_frame.pack(fill="x", **pad)
        self.file_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_var, width=48).pack(side="left")
        tk.Button(file_frame, text="Browse", command=self.browse).pack(side="left", padx=6)

        # Progress bar
        self.progress = ttk.Progressbar(root, length=520, mode="determinate")
        self.progress.pack(**pad)

        # Status label
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status_var, anchor="w", fg="gray").pack(fill="x", **pad)

        # Log box
        self.log = tk.Text(root, height=6, state="disabled", bg="#f5f5f5", font=("Courier", 9))
        self.log.pack(fill="x", **pad)

        # Import button
        tk.Button(root, text="Import to Supabase", command=self.start_import,
                  bg="#3ecf8e", fg="white", font=("Arial", 11, "bold"),
                  height=2).pack(fill="x", padx=16, pady=8)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            self.file_var.set(path)

    def log_msg(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_import(self):
        key = self.key_var.get().strip()
        path = self.file_var.get().strip()

        if not key:
            messagebox.showerror("Missing Key", "Please enter your Supabase service role key.")
            return
        if not path:
            messagebox.showerror("Missing File", "Please select an Excel file.")
            return

        threading.Thread(target=self.run_import, args=(key, path), daemon=True).start()

    def run_import(self, key, path):
        try:
            self.status_var.set("Reading Excel file...")
            self.log_msg(f"Loading: {path}")
            df = pd.read_excel(path)
            self.log_msg(f"Found {len(df)} rows, {len(df.columns)} columns")

            df = df.rename(columns=COLUMN_MAP)
            mapped_cols = [c for c in COLUMN_MAP.values() if c in df.columns]
            df = df[mapped_cols]
            df["uid"] = [str(uuid.uuid4()) for _ in range(len(df))]
            df["created_at"] = datetime.utcnow().isoformat()
            import math

            INTEGER_COLS = ["pos_matched", "neg_matched", "pos_scan", "neg_scan",
                            "pos_h_scan", "pos_nh4_scan", "pos_na_scan", "pos_k_scan",
                            "neg_mh_scan", "neg_cl_scan", "neg_hcoo_scan", "neg_ch3coo_scan"]

            def to_int(x):
                if x is None: return None
                s = str(x).strip().lower()
                if s == "yes": return 1
                if s == "no": return 0
                if s in ("nan", "none", ""): return None
                try: return int(float(s))
                except: return None

            for col in INTEGER_COLS:
                if col in df.columns:
                    df[col] = df[col].map(to_int)

            INT_KEYS = set(INTEGER_COLS)
            REAL_KEYS = {c for c in df.columns if c not in INT_KEYS and c not in ("uid", "created_at", "compound_id", "chrom_id", "name", "formula", "pos_adduct", "neg_adduct", "pos_frags", "neg_frags", "pos_all_frags", "neg_all_frags", "pos_h_frags", "pos_nh4_frags", "pos_na_frags", "pos_k_frags", "neg_mh_frags", "neg_cl_frags", "neg_hcoo_frags", "neg_ch3coo_frags", "compound_class")}

            def clean(k, v):
                if v is None:
                    return None
                if isinstance(v, float):
                    if math.isnan(v) or math.isinf(v):
                        return None
                    if k in INT_KEYS:
                        return int(v)
                if k in REAL_KEYS:
                    try:
                        return float(v)
                    except (ValueError, TypeError):
                        return None
                return v

            records_raw = df.to_dict(orient="records")
            records = [{k: clean(k, v) for k, v in row.items()} for row in records_raw]

            # Debug: log unique values in each column to spot bad data
            for col in df.columns:
                uniq = df[col].dropna().unique()[:5]
                self.log_msg(f"  {col}: {list(uniq)}")

            self.log_msg(f"Connecting to Supabase...")
            client = create_client(SUPABASE_URL, key)

            total = len(records)
            BATCH = 500
            self.progress["maximum"] = total

            for i in range(0, total, BATCH):
                batch = records[i:i + BATCH]
                client.table("compounds").insert(batch).execute()
                done = min(i + BATCH, total)
                self.progress["value"] = done
                self.status_var.set(f"Inserted {done}/{total} rows...")
                self.log_msg(f"  Batch {i//BATCH + 1}: {done}/{total} rows inserted")
                self.root.update_idletasks()

            self.status_var.set(f"Done! {total} rows imported successfully.")
            self.log_msg("Import complete!")
            messagebox.showinfo("Success", f"{total} compounds imported successfully!")

        except Exception as e:
            self.status_var.set("Error — see log.")
            self.log_msg(f"ERROR: {e}")
            messagebox.showerror("Import Failed", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ImportApp(root)
    root.mainloop()
