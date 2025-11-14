#!/usr/bin/env python3
"""
Desktop Casting Viewer GUI
Displays up to 8 incoming screen streams in a grid layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
import sys
import importlib.util
import os

# Import server module - handle both development and PyInstaller bundled mode
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in development
    base_path = os.path.dirname(os.path.abspath(__file__))

server_path = os.path.join(base_path, "server.py")
spec = importlib.util.spec_from_file_location("server", server_path)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

stream_manager = server_module.stream_manager


class StreamViewer:
    """Main GUI application for viewing multiple streams"""

    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Casting Receiver - Monitoring Station")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#1e1e1e")

        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create header
        self.create_header()

        # Create stream grid
        self.stream_frames = {}
        self.stream_labels = {}
        self.stream_name_labels = {}
        self.create_stream_grid()

        # Server status
        self.server_running = False
        self.server_thread = None

        # Update loop
        self.running = True
        self.update_streams()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_header(self):
        """Create the header bar with controls"""
        header = tk.Frame(self.root, bg="#2d2d2d", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)

        # Title
        title = tk.Label(
            header,
            text="🖥️ Desktop Casting Receiver",
            font=("Arial", 18, "bold"),
            fg="#ffffff",
            bg="#2d2d2d"
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)

        # Status
        self.status_label = tk.Label(
            header,
            text="● Server Stopped",
            font=("Arial", 12),
            fg="#e74c3c",
            bg="#2d2d2d"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Stream count
        self.count_label = tk.Label(
            header,
            text="Active Streams: 0/8",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#2d2d2d"
        )
        self.count_label.pack(side=tk.LEFT, padx=10)

        # Server control button
        self.server_btn = tk.Button(
            header,
            text="Start Server",
            command=self.toggle_server,
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.server_btn.pack(side=tk.RIGHT, padx=20, pady=10)

        # Info button
        info_btn = tk.Button(
            header,
            text="ℹ Info",
            command=self.show_info,
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        info_btn.pack(side=tk.RIGHT, padx=5, pady=10)

    def create_stream_grid(self):
        """Create a 2x4 grid for displaying streams"""
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights for responsive layout
        for i in range(2):  # 2 rows
            container.grid_rowconfigure(i, weight=1)
        for i in range(4):  # 4 columns
            container.grid_columnconfigure(i, weight=1)

        # Create 8 stream slots
        for i in range(8):
            row = i // 4
            col = i % 4

            # Create frame for each stream
            frame = tk.Frame(container, bg="#2d2d2d", relief=tk.RAISED, borderwidth=2)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # Name label
            name_label = tk.Label(
                frame,
                text=f"Slot {i+1}: Waiting...",
                font=("Arial", 11, "bold"),
                fg="#95a5a6",
                bg="#2d2d2d",
                anchor="w"
            )
            name_label.pack(fill=tk.X, padx=5, pady=5)

            # Video display label
            label = tk.Label(frame, bg="#000000")
            label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

            # Status label
            status_label = tk.Label(
                frame,
                text="No connection",
                font=("Arial", 9),
                fg="#7f8c8d",
                bg="#2d2d2d"
            )
            status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

            self.stream_frames[i] = frame
            self.stream_labels[i] = label
            self.stream_name_labels[i] = (name_label, status_label)

    def toggle_server(self):
        """Start or stop the server"""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        """Start the WebRTC server in a separate thread"""
        try:
            self.server_thread = threading.Thread(
                target=server_module.run_server,
                args=('0.0.0.0', 8080),
                daemon=True
            )
            self.server_thread.start()
            self.server_running = True

            self.status_label.config(text="● Server Running", fg="#27ae60")
            self.server_btn.config(text="Stop Server", bg="#e74c3c")

            # Get local IP
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            except:
                local_ip = "localhost"
            finally:
                s.close()

            messagebox.showinfo(
                "Server Started",
                f"Server is running!\n\n"
                f"Chromebooks should visit:\n"
                f"https://{local_ip}:8080\n\n"
                f"Important: You'll need to accept the\n"
                f"self-signed certificate warning in the browser.\n"
                f"Click 'Advanced' then 'Proceed to {local_ip}'.\n\n"
                f"Make sure devices are on the same network."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")

    def stop_server(self):
        """Stop the server (requires app restart)"""
        response = messagebox.askyesno(
            "Stop Server",
            "Stopping the server requires restarting the application.\n"
            "Do you want to restart now?"
        )
        if response:
            self.on_closing()

    def show_info(self):
        """Show information dialog"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = "localhost"
        finally:
            s.close()

        messagebox.showinfo(
            "Desktop Casting Receiver",
            f"This application receives desktop streams from Chromebooks.\n\n"
            f"Setup Instructions:\n"
            f"1. Click 'Start Server' if not running\n"
            f"2. On each Chromebook, open a browser\n"
            f"3. Visit: https://{local_ip}:8080\n"
            f"4. Accept certificate warning (Advanced > Proceed)\n"
            f"5. Enter a name and click 'Start Sharing Screen'\n"
            f"6. Select the screen to share\n\n"
            f"Maximum simultaneous streams: 8\n\n"
            f"Note: All devices must be on the same network."
        )

    def update_streams(self):
        """Update all stream displays"""
        if not self.running:
            return

        try:
            streams = stream_manager.get_all_streams()
            active_count = len(streams)

            # Update count
            self.count_label.config(text=f"Active Streams: {active_count}/8")

            # Get client IDs in sorted order
            client_ids = sorted(streams.keys())

            # Update each slot
            for slot_idx in range(8):
                if slot_idx < len(client_ids):
                    client_id = client_ids[slot_idx]
                    stream_data = streams[client_id]
                    frame = stream_data['frame']
                    name = stream_data['name']

                    if frame is not None:
                        # Resize frame to fit label
                        label = self.stream_labels[slot_idx]
                        label_width = label.winfo_width() or 400
                        label_height = label.winfo_height() or 300

                        # Calculate scaling to fit while maintaining aspect ratio
                        h, w = frame.shape[:2]
                        scale = min(label_width / w, label_height / h)
                        new_w = int(w * scale * 0.95)
                        new_h = int(h * scale * 0.95)

                        if new_w > 0 and new_h > 0:
                            resized = cv2.resize(frame, (new_w, new_h))

                            # Convert to PIL Image
                            img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(img)
                            img_tk = ImageTk.PhotoImage(image=img)

                            # Update label
                            label.configure(image=img_tk)
                            label.image = img_tk  # Keep a reference

                        # Update name
                        name_label, status_label = self.stream_name_labels[slot_idx]
                        name_label.config(text=f"Slot {slot_idx+1}: {name}", fg="#3498db")
                        status_label.config(text="● Connected", fg="#27ae60")
                    else:
                        # No frame yet
                        name_label, status_label = self.stream_name_labels[slot_idx]
                        name_label.config(text=f"Slot {slot_idx+1}: {name}", fg="#3498db")
                        status_label.config(text="Connecting...", fg="#f39c12")
                else:
                    # Empty slot
                    name_label, status_label = self.stream_name_labels[slot_idx]
                    name_label.config(text=f"Slot {slot_idx+1}: Waiting...", fg="#95a5a6")
                    status_label.config(text="No connection", fg="#7f8c8d")

                    # Clear image
                    self.stream_labels[slot_idx].configure(image='')

        except Exception as e:
            print(f"Error updating streams: {e}")

        # Schedule next update
        self.root.after(100, self.update_streams)  # Update at ~10 FPS

    def on_closing(self):
        """Handle window close"""
        self.running = False
        self.root.quit()
        sys.exit(0)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = StreamViewer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
