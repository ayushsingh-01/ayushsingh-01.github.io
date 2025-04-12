import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import { GoogleGenerativeAI } from "@google/generative-ai";

const app = express();
const port = 3000;

const genAI = new GoogleGenerativeAI("AIzaSyCc4i9uOEyCQomrIAE9kSq-f1S7tkwVWN0"); // Replace with your actual API key

app.use(cors());
app.use(bodyParser.json());

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message;
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });
    const result = await model.generateContent(userMessage);
    const response = await result.response;
    res.json({ reply: response.text() });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ reply: "Something went wrong!" });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
