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

from ..common import get_logger, get_config, get_local_ip

logger = get_logger(__name__)


class StreamViewer:
    """Main GUI application for viewing multiple streams"""

    def __init__(self, root, stream_manager, server_runner=None, config=None):
        """
        Initialize the stream viewer

        Args:
            root: Tkinter root window
            stream_manager: StreamManager instance
            server_runner: Callable to start the server (optional)
            config: GUI configuration (optional)
        """
        self.root = root
        self.stream_manager = stream_manager
        self.server_runner = server_runner
        self.config = config or get_config().gui

        self.root.title(self.config.window_title)
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
        self.stream_container = None
        self.current_stream_count = 0

        # Expanded view state
        self.expanded_client_id = None
        self.expanded_frame = None
        self.expanded_label = None

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

    def create_stream_grid(self, client_ids=None):
        """Create a dynamic grid for displaying only connected streams"""
        # Destroy existing container if it exists
        if self.stream_container:
            self.stream_container.destroy()

        # Clear dictionaries
        self.stream_frames.clear()
        self.stream_labels.clear()
        self.stream_name_labels.clear()

        # If no clients, show a message
        if not client_ids:
            self.stream_container = tk.Frame(self.root, bg="#1e1e1e")
            self.stream_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

            no_stream_label = tk.Label(
                self.stream_container,
                text="No active connections\n\nWaiting for Chromebooks to connect...",
                font=("Arial", 16),
                fg="#7f8c8d",
                bg="#1e1e1e"
            )
            no_stream_label.pack(expand=True)
            self.current_stream_count = 0
            return

        num_streams = len(client_ids)
        self.current_stream_count = num_streams

        # Calculate grid dimensions (try to make it as square as possible)
        if num_streams == 1:
            rows, cols = 1, 1
        elif num_streams == 2:
            rows, cols = 1, 2
        elif num_streams <= 4:
            rows, cols = 2, 2
        elif num_streams <= 6:
            rows, cols = 2, 3
        elif num_streams <= 9:
            rows, cols = 3, 3
        elif num_streams <= 12:
            rows, cols = 3, 4
        else:
            rows, cols = 4, 4

        container = tk.Frame(self.root, bg="#1e1e1e")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.stream_container = container

        # Configure grid weights for responsive layout
        for i in range(rows):
            container.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            container.grid_columnconfigure(i, weight=1)

        # Create slots for each connected stream
        for idx, client_id in enumerate(client_ids):
            row = idx // cols
            col = idx % cols

            # Create frame for each stream
            frame = tk.Frame(container, bg="#2d2d2d", relief=tk.RAISED, borderwidth=2, cursor="hand2")
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # Name label
            name_label = tk.Label(
                frame,
                text=f"Connecting...",
                font=("Arial", 11, "bold"),
                fg="#95a5a6",
                bg="#2d2d2d",
                anchor="w"
            )
            name_label.pack(fill=tk.X, padx=5, pady=5)

            # Video display label
            label = tk.Label(frame, bg="#000000", cursor="hand2")
            label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

            # Status label
            status_label = tk.Label(
                frame,
                text="Connecting...",
                font=("Arial", 9),
                fg="#7f8c8d",
                bg="#2d2d2d"
            )
            status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

            # Store references with client_id as key
            self.stream_frames[client_id] = frame
            self.stream_labels[client_id] = label
            self.stream_name_labels[client_id] = (name_label, status_label)

            # Bind click event to expand this stream
            frame.bind("<Button-1>", lambda e, cid=client_id: self.toggle_expand(cid))
            label.bind("<Button-1>", lambda e, cid=client_id: self.toggle_expand(cid))
            name_label.bind("<Button-1>", lambda e, cid=client_id: self.toggle_expand(cid))
            status_label.bind("<Button-1>", lambda e, cid=client_id: self.toggle_expand(cid))

    def toggle_expand(self, client_id):
        """Toggle expanded view for a stream"""
        if self.expanded_client_id == client_id:
            # Already expanded, collapse it
            self.collapse_stream()
        else:
            # Expand this stream
            self.expand_stream(client_id)

    def expand_stream(self, client_id):
        """Expand a stream to full window"""
        # Store current state
        self.expanded_client_id = client_id

        # Destroy the grid container
        if self.stream_container:
            self.stream_container.destroy()

        # Create expanded view
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.stream_container = container

        # Create frame for expanded stream
        frame = tk.Frame(container, bg="#2d2d2d", relief=tk.RAISED, borderwidth=2, cursor="hand2")
        frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Get stream data
        streams = self.stream_manager.get_all_streams()
        stream_data = streams.get(client_id, {})
        name = stream_data.get('name', 'Unknown')

        # Name label
        name_label = tk.Label(
            frame,
            text=f"{name} (click to minimize)",
            font=("Arial", 16, "bold"),
            fg="#3498db",
            bg="#2d2d2d",
            anchor="w"
        )
        name_label.pack(fill=tk.X, padx=10, pady=10)

        # Video display label
        label = tk.Label(frame, bg="#000000", cursor="hand2")
        label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Bind click to collapse
        frame.bind("<Button-1>", lambda e: self.collapse_stream())
        label.bind("<Button-1>", lambda e: self.collapse_stream())
        name_label.bind("<Button-1>", lambda e: self.collapse_stream())

        # Store references
        self.expanded_frame = frame
        self.expanded_label = label

    def collapse_stream(self):
        """Collapse expanded stream back to grid view"""
        self.expanded_client_id = None
        self.expanded_frame = None
        self.expanded_label = None

        # Rebuild the grid with current streams
        streams = self.stream_manager.get_all_streams()
        client_ids = sorted(streams.keys())
        self.create_stream_grid(client_ids)

    def toggle_server(self):
        """Start or stop the server"""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        """Start the WebRTC server in a separate thread"""
        if not self.server_runner:
            messagebox.showerror("Error", "Server runner not configured")
            return

        try:
            self.server_thread = threading.Thread(
                target=self.server_runner,
                daemon=True
            )
            self.server_thread.start()
            self.server_running = True

            self.status_label.config(text="● Server Running", fg="#27ae60")
            self.server_btn.config(text="Stop Server", bg="#e74c3c")

            # Get local IP
            local_ip = get_local_ip() or "localhost"

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
            streams = self.stream_manager.get_all_streams()
            active_count = len(streams)
            client_ids = sorted(streams.keys())

            # Update count label
            self.count_label.config(text=f"Active Streams: {active_count}")

            # Check if we need to rebuild the grid (stream count changed)
            if not self.expanded_client_id and active_count != self.current_stream_count:
                self.create_stream_grid(client_ids if active_count > 0 else None)

            # If in expanded view, update only the expanded stream
            if self.expanded_client_id:
                # Check if expanded stream still exists
                if self.expanded_client_id not in streams:
                    # Stream disconnected, collapse back to grid
                    self.collapse_stream()
                else:
                    # Update the expanded view
                    stream_data = streams[self.expanded_client_id]
                    frame = stream_data['frame']

                    if frame is not None and self.expanded_label:
                        # Resize frame to fit label
                        label_width = self.expanded_label.winfo_width() or 800
                        label_height = self.expanded_label.winfo_height() or 600

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
                            self.expanded_label.configure(image=img_tk)
                            self.expanded_label.image = img_tk  # Keep a reference
            else:
                # Grid view - update all streams
                for client_id in client_ids:
                    if client_id in self.stream_labels:
                        stream_data = streams[client_id]
                        frame = stream_data['frame']
                        name = stream_data['name']

                        if frame is not None:
                            # Resize frame to fit label
                            label = self.stream_labels[client_id]
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

                            # Update name and status
                            if client_id in self.stream_name_labels:
                                name_label, status_label = self.stream_name_labels[client_id]
                                name_label.config(text=f"{name}", fg="#3498db")
                                status_label.config(text="● Connected", fg="#27ae60")
                        else:
                            # No frame yet
                            if client_id in self.stream_name_labels:
                                name_label, status_label = self.stream_name_labels[client_id]
                                name_label.config(text=f"{name}", fg="#3498db")
                                status_label.config(text="Connecting...", fg="#f39c12")

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
