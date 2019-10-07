"""
Tested with Python v3.7.3
Copyright 2019 Zoran Petrovic (zoran@zoran-software.com)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""

import json
import os
import tkinter as tk
from tkinter import Checkbutton, Entry, Label, messagebox
from tkinter import ttk as ttk
from tkinter.scrolledtext import ScrolledText
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AppFrame(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.is_content_html = tk.BooleanVar()
        self.is_send_bulk = tk.BooleanVar()
        self.message = ""
        self.initUI(root)

    def initUI(self, root):

        root.title("SendGrid V3 GUI Client v1.0")

        Label(root, text="SendGrid API key:").pack(anchor=tk.W)
        self.ui_api_key = Entry(root)
        self.ui_api_key.pack(fill=tk.X)

        Label(root, text="Sender email:").pack(anchor=tk.W)
        self.ui_email_from = Entry(root)
        self.ui_email_from.pack(fill=tk.X)

        Label(root, text="Recipient email (separate emails by ; if many):").pack(anchor=tk.W)
        self.ui_emails_to = Entry(root)
        self.ui_emails_to.pack(fill=tk.X)

        Label(root, text="Carbon copy recipient email (separate emails by ; if many):").pack(anchor=tk.W)
        self.ui_emails_cc = Entry(root)
        self.ui_emails_cc.pack(fill=tk.X)

        Label(root, text="Subject:").pack(anchor=tk.W)
        self.ui_subject = Entry(root)
        self.ui_subject.pack(fill=tk.X)

        Label(root, text="Content:").pack(anchor=tk.W)
        self.ui_content = ScrolledText(root)
        self.ui_content.pack(fill=tk.BOTH)

        self.ui_is_content_html = Checkbutton(root, text="Content is HTML",
                                              onvalue=True, offvalue=False, var=self.is_content_html)
        self.ui_is_content_html.select()
        self.ui_is_content_html.pack(anchor=tk.W)

        self.ui_is_send_bulk = Checkbutton(root, text="Send to all recipients in single email",
                                           onvalue=True, offvalue=False, var=self.is_send_bulk)
        self.ui_is_send_bulk.pack(anchor=tk.W)

        ttk.Button(root, text="Send", command=self.send).pack(fill=tk.BOTH)

        Label(root, text="Copyright 2019 Zoran Petrovic\nLicence: GNU General Public License").pack(fill=tk.BOTH)

    def send(self):
        # Prepare input.
        emails_to_list = self.ui_emails_to.get().split(";")
        emails_cc_list = self.ui_emails_cc.get().split(";") if len(self.ui_emails_cc.get()) > 0 else None

        if emails_cc_list and (set(emails_to_list) & set(emails_cc_list)):
            tk.messagebox.showerror("Error", "Recipient email cannot be listed in carbon copy recipients!")
            return

        subject = self.ui_subject.get()
        content_type = "text/html" if self.is_content_html.get() else "text/plain"
        content = self.ui_content.get("1.0", "end-1c")
        email_from = self.ui_email_from.get().strip()
        personalizations = [{}]

        if emails_cc_list:
            personalizations[0].update({"cc": [{"email": x.strip()} for x in emails_cc_list]})

        if self.is_send_bulk.get():
            emails_to = [{"email": x.strip()} for x in emails_to_list]
            personalizations[0].update({"to": emails_to})
            self._send(subject, content_type, content, email_from, personalizations)
        else:
            for email in emails_to_list:
                personalizations[0].update({"to": [{"email": email.strip()}]})
                self._send(subject, content_type, content, email_from, personalizations)
        tk.messagebox.showinfo("Done", self.message)
        self.message = ""

    def _send(self, subject, content_type, content, email_from, personalizations):
        try:
            self.message += "\n" + str(personalizations[0]["to"])
            body = {
                "personalizations": personalizations,
                "from": {"email": email_from},
                "subject": subject,
                "content": [{"type": content_type, "value": content}]
            }
            url = "https://api.sendgrid.com/v3/mail/send"
            request = Request(url)
            request.add_header("Content-Type", "application/json; charset=utf-8")
            request.add_header("authorization", "Bearer {}".format(self.ui_api_key.get()))
            json_data_as_bytes = json.dumps(body).encode("utf-8")  # Must be bytes
            request.add_header("Content-Length", len(json_data_as_bytes))
            response = urlopen(request, json_data_as_bytes)
        except HTTPError as e:
            self.message += "\nHTTPError: {}".format(e.code)
        except URLError as e:
            self.message += "\nURLError: {}".format(e.reason)
        except Exception as e:
            self.message += "\nError", str(e)
        else:
            self.message += "\nStatus code: {}".format(response.getcode())


if __name__ == "__main__":
    root = tk.Tk()
    AppFrame(root)
    root.mainloop()
