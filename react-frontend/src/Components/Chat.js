import React, { useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import ScrollToBottom from "react-scroll-to-bottom";
import "./chat.css";

import { io } from "socket.io-client";

let socket;

function Chat() {
	// Define an initial Message to greet the user
	const initialMsg = [
		"Hello, welcome to Closet.AI. Please tell me about your day 😊",
		getTime(),
		"bot",
		"text",
	];

	// Define the abort Message
	const abortMsg = [
		"You can interrupt the process at any time by typing 'reset' into the Chat 🤯",
		getTime(),
		"bot",
		"text",
	];

	// Maximum File Size a User Image can have in MB (MUST MATCH SETTINGS IN SERVER)
	let maxFileSize = 5;

	// Define the State that the input is stored in as an empty String
	const [msgInput, setMsgInput] = useState("");

	// Define the State that the Messages are stored in as an empty Array
	const [messages, setMessages] = useState([initialMsg, abortMsg]);

	// Define that State that the USers Image is stored in
	const [usrImage, setUsrImage] = useState(["none", 0]);

	// Storing information about what categories are selected
	const [clickCategory, setClickCategory] = useState([]);

	// helper to make selected clothing piece visible
	const [selectedID, setSelectedId] = useState();

	// Create a new Datatype to Store all necessary information about a Message
	class Message {
		constructor(msgContent, msgTime, msgUser, msgType, category) {
			// A message should ALWAYS contain the following Information in the same order:
			// The content of the message
			this.msgContent = msgContent;
			// The time the message was sent
			this.msgTime = msgTime;
			// Should either be "user" or "bot"
			this.msgUser = msgUser;
			// Should either be "text" or "image" or "selectableImage"
			this.msgType = msgType;
			// Should either be "top" or "shoes" or "pants"
			this.category = category;

			return { msgContent, msgTime, msgUser, msgType, category };
		}
	}

	// This receives new messages from the Server via socket listening and stores them in the messages state.
	useEffect(() => {
		socket = io();

		socket.on("chat", (data) => {
			setMessages((current) => [
				...current,
				[
					data.msgContent,
					data.msgTime,
					data.msgSender,
					data.msgType,
					data.category,
				],
			]);
		});

		return () => {
			socket.disconnect();
		};
	}, []);

	// Define a function that returns the current time
	function getTime() {
		let currentDate = new Date();
		let time =
			currentDate.getHours() +
			":" +
			currentDate.getMinutes() +
			":" +
			currentDate.getSeconds();

		return time;
	}

	// Inspiration for the input field was found in the following two videos:
	// https://www.youtube.com/watch?v=IkMND33x0qQ&t=176s&ab_channel=TheNetNinja
	// https://www.youtube.com/watch?v=pJiRj02PkJQ&ab_channel=TheNetNinja
	function handleTextSubmit(e) {
		// Prevents the page from being refreshed every time the button gets pressed
		e.preventDefault();

		let message = new Message();
		message.msgContent = msgInput.toString();
		message.msgTime = getTime();
		message.msgSender = "user";
		message.msgType = "text";

		// Clear the input field after the message has been sent
		setMsgInput("");

		// Adds the User Message to the array of messages
		setMessages((current) => [
			...current,
			[message.msgContent, message.msgTime, message.msgSender, message.msgType],
		]);

		// Send the message to the server via client/socket communication
		socket.emit("chat", JSON.stringify(message));

		if (msgInput === "reset") {
			setMessages([initialMsg, abortMsg]);
			setMsgInput("");
			setSelectedId();
			setClickCategory([]);
		}
	}

	// Inspiration for this was found on the official documentation of the package:
	// https://react-dropzone.js.org/
	const { getRootProps, getInputProps } = useDropzone({
		// Specify the accepted file types; in this case all image types
		accept: "image/*",
		onDrop: (acceptedFiles) => {
			// Create a new FileReader to transform the content into a readable object
			// This encoding Method is called Base64 and converts objects into Strings
			let reader = new FileReader();
			// This takes the first file and scraps the rest
			reader.readAsDataURL(acceptedFiles[0]);

			// Update the State
			reader.onload = () => {
				setUsrImage([reader.result, usrImage[1] + 1]);
			};
		},
	});

	// Instantly submits an image as soon as the user selects it
	useEffect(() => {
		if (usrImage[0] !== "none") {
			handleImageSubmit();
		}
	}, [usrImage]);

	// Code Reference: https://codepen.io/jdeagle/pen/DgGxBq
	function dataURLtoBlob(dataURL) {
		//http://mitgux.com/send-canvas-to-server-as-file-using-ajax
		// Decode the dataURL
		var binary = atob(dataURL.split(",")[1]);
		// Create 8-bit unsigned array
		var array = [];
		for (var i = 0; i < binary.length; i++) {
			array.push(binary.charCodeAt(i));
		}
		// Return our Blob object
		return new Blob([new Uint8Array(array)], { type: "image/png" });
	}

	function handleImageSubmit() {
		let message = new Message();
		// Cuts the "data:image/png;base64," part of the encoded String so the backend can decode it instantly
		var image = usrImage[0];
		message.msgContent = image.split(",").pop();
		message.msgTime = getTime();
		message.msgSender = "user";
		message.msgType = "image";

		// Adds the User Message to the array of messages
		setMessages((current) => [
			...current,
			[image, message.msgTime, message.msgSender, message.msgType],
		]);

		// restarts
		setClickCategory([]);

		// Determine fileSize of usrImage
		let file = dataURLtoBlob(usrImage[0]);
		let fileSize = file.size;

		if (fileSize > maxFileSize * 1048576) {
			const msg = [
				"File Size too big! Please only use Images smaller than " +
					maxFileSize +
					"MB",
				getTime(),
				"bot",
				"text",
			];
			setMessages((current) => [...current, msg]);
		} else {
			socket.emit("upload", JSON.stringify(message));
		}
	}

	function handleImageSelection(image, category, id) {
		if (!clickCategory.includes(category)) {
			setSelectedId(id);
			setClickCategory([...clickCategory, category]);
			socket.emit("select", image, category);
		}
	}

	return (
		<div className="wrapper">
			<div className="container">
				<div className="header">
					<h1>CLOSET.AI</h1>
				</div>
				<ScrollToBottom className="body">
					{/* Go through the array and display every message either as user or as bot message */}
					{messages.map((message, index) => {
						if (message[2] === "bot") {
							if (message[3] === "selectableImage") {
								return (
									<img
										/* Add image as URL */
										src={message[0]}
										key={index}
										// Check if the image has already been clicked
										className={
											selectedID === index ? "image selected" : "image"
										}
										alt="imageDisplayError"
										onClick={() => {
											handleImageSelection(message[0], message[4], index);
										}}
									></img>
								);
							}
							if (message[3] === "image") {
								return (
									<img
										/* Add image as URL */
										src={message[0]}
										key={index}
										className="image botImage"
										alt="imageDisplayError"
									></img>
								);
							}
							return (
								<p className="message botMessage" key={index}>
									{message[0]}
								</p>
							);
						} else {
							if (message[3] === "image") {
								return (
									<img
										src={message[0]}
										key={index}
										className="image usrImage"
										alt="imageDisplayError"
									></img>
								);
							} else {
								return (
									<p className="message usrMessage" key={index}>
										{message[0]}
									</p>
								);
							}
						}
					})}
				</ScrollToBottom>
				<div className="footer">
					<form onSubmit={handleTextSubmit}>
						<input
							className="textInput"
							type="text"
							required
							value={msgInput}
							onChange={(e) => setMsgInput(e.target.value)}
						/>
						<button className="sendButton">SEND</button>
					</form>
					<span className="hiddenFileInput" {...getRootProps()}>
						<input {...getInputProps()} />
					</span>
				</div>
			</div>
		</div>
	);
}
export default Chat;
