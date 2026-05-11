from flask import Flask, request

app = Flask(__name__)

PASSWORD = "jamal123"

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Kado Rahasia</title>

    <style>
        body {
            background: #0f172a;
            font-family: Arial;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .box {
            background: #1e293b;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            width: 320px;
        }

        input {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: none;
            margin-top: 10px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            margin-top: 10px;
            background: #22c55e;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        .gift {
            font-size: 100px;
            margin-top: 20px;
        }

        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>

<div class="box">
    <h1>🎁 Kado Rahasia</h1>

    <form method="POST">
        <input type="password" name="password" placeholder="Masukkan password">
        <button type="submit">Buka Kado</button>
    </form>

    %%CONTENT%%

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    content = ""

    if request.method == "POST":
        password = request.form.get("password")

        if password == PASSWORD:
            content = """
            <div class="gift">🎁</div>
            <h2>Selamat! Kadonya terbuka 🎉</h2>
            """
        else:
            content = '<div class="error">Password salah!</div>'

    return HTML.replace("%%CONTENT%%", content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)