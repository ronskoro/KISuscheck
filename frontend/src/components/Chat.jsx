import { useEffect, useState } from "react";
import { IoMdSend } from "react-icons/io";
import { BiBot, BiUser } from "react-icons/bi";
import "./chat.css";

const Chat = () => {
  const [chat, setChat] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [botTyping, setbotTyping] = useState(false);
  const name = "Test";

  useEffect(() => {
    const request_temp = {
      sender: "bot",
      sender_id: name,
      msg: "Hi, I’m Eco! 👋I’m a sustainable nutritional bot. I can help you get information about a product or I can give you recommendations for food. What would you like to do? 👀",
    };

    setChat([...chat, request_temp]);
  }, []);

  useEffect(() => {
    // const objDiv = document.getElementById("messageArea");
    // objDiv.scrollTop = objDiv.scrollHeight;

    setTimeout(() => {
      var objDiv = document.getElementById("messageArea");
      objDiv.lastChild.scrollIntoView({ behavior: "smooth" });
    }, 50);
  }, [chat]);

  const handleSubmit = (evt) => {
    evt.preventDefault();

    const request_temp = { sender: "user", sender_id: name, msg: inputMessage };

    if (inputMessage !== "") {
      setChat((chat) => [...chat, request_temp]);
      setbotTyping(true);
      setInputMessage("");
      rasaAPI(name, inputMessage);
    } else {
      window.alert("Please enter valid message");
    }
  };

  const rasaAPI = async function handleClick(name, msg) {
    await fetch("http://localhost:5005/webhooks/rest/webhook", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        charset: "UTF-8",
      },
      credentials: "same-origin",
      body: JSON.stringify({ sender: name, message: msg }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (response) {
          const chatTemp = [];

          for (const { recipient_id, text, image, buttons } of response) {
            const msg = text || image || null;

            const response_temp = {
              sender: "bot",
              recipient_id,
              msg,
              buttons,
            };

            chatTemp.push(response_temp);
          }
          setChat((chat) => [...chat, ...chatTemp]);
          setbotTyping(false);
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div className="h-screen lg:px-60 lg:py-4 lg:bg-slate-900">
      <div className="lg:rounded-lg lg:border-2 lg:border-black">
        <div className="bg-green-700 lg:rounded-t-lg h-[100px]">
          <h1 className="text-4xl text-center pt-4 font-bold text-slate-900">
            KI-SusCheck
          </h1>
          {botTyping ? <h6 className="text-center">Bot Typing....</h6> : null}
        </div>
        <div
          className="h-[calc(100vh-200px)] lg:h-[calc(100vh-200px-30px)] p-4 overflow-y-auto bg-[#FFFFFF]"
          id="messageArea"
        >
          {chat.map((user, key) => (
            <div
              key={key}
              className={chat[key + 1]?.sender !== "bot" ? "mb-2" : undefined}
            >
              {user.sender === "bot" ? (
                <div
                  className={
                    key === 0
                      ? "flex items-center gap-x-2 bg-slate-300 px-3 pt-3 rounded-t-lg pb-3 rounded-b-lg"
                      : chat[key + 1]?.sender !== "bot"
                      ? "flex items-center gap-x-2 bg-slate-300 px-3 pb-3 rounded-b-lg"
                      : "flex items-center gap-x-2 bg-slate-300 px-3 pb-3"
                  }
                >
                  {chat[key - 1]?.sender !== "bot" ? (
                    <BiBot className="border-2 border-slate-900 rounded-full p-1 text-4xl min-w-[35px]" />
                  ) : (
                    <div className="pl-9" />
                  )}
                  <h5 className="bg-green-100 rounded-lg py-2 px-3">
                    {user.msg && /\bhttps?:\/\/\S+/i.test(user.msg) ? (
                      /\.(gif|jpe?g|tiff?|png|webp|bmp)$/i.test(user.msg) ? (
                        <img src={user.msg} alt="img" className="w-40" />
                      ) : (
                        <a
                          href={user.msg}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {user.msg}
                        </a>
                      )
                    ) : (
                      user.msg
                    )}
                    {user.buttons && (
                      <div className="space-x-2">
                        {user.buttons.map((button, key) => (
                          <button
                            key={key}
                            className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg"
                            onClick={() => {
                              setbotTyping(true);
                              rasaAPI(name, button.payload);
                            }}
                          >
                            {button.title}
                          </button>
                        ))}
                      </div>
                    )}
                  </h5>
                </div>
              ) : (
                <div className="flex justify-end items-center gap-x-2 bg-slate-300 px-3 pt-3 rounded-t-lg">
                  <h5 className="bg-yellow-100 rounded-lg py-2 px-3 mb-2">
                    {user.msg}
                  </h5>
                  <BiUser className="border-2 border-slate-900 rounded-full p-1 text-4xl min-w-[35px]" />
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="bg-green-700 lg:rounded-b-lg h-[100px] px-2 lg:px-40">
          <form
            className="flex items-center justify-center gap-x-2 h-full"
            onSubmit={handleSubmit}
          >
            <div className="h-1/2 w-full">
              <input
                placeholder="Type your message here..."
                onChange={(e) => setInputMessage(e.target.value)}
                value={inputMessage}
                type="text"
                className="w-full h-full border-slate-900 rounded-lg p-2"
              ></input>
            </div>
            <div>
              <button
                type="submit"
                disabled={botTyping}
                className="disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <IoMdSend className="border-2 border-slate-900 rounded-full p-1 text-4xl hover:bg-yellow-400 bg-green-500" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
