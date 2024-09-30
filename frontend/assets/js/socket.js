const socket = io.connect("http://127.0.0.1:8009");

// Lắng nghe sự kiện connect
socket.on("connect", () => {
    console.log("Connected to server: " + socket.id);
    // Tham gia vào phòng "temperature_room"
    socket.emit("join_room", "temperature");
    socket.emit("join_room", "hudmidity");
});
// Lắng nghe sự kiện my response từ server
socket.on("my response", (data) => {
    console.log("Received data:", data);
    const messageDiv = document.getElementById("messages");
    const newMessage = document.createElement("p");
    newMessage.textContent = `Received: ${data}`;
    messageDiv.appendChild(newMessage);
});

// Lắng nghe sự kiện disconnect
socket.on("disconnect", () => {
    console.log("Disconnected from server");
});