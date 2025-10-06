from flask import Flask, render_template, request, jsonify
import re
import json

app = Flask(__name__)

class QuizConverter:
    def parse_txt_content(self, txt_content):
        try:
            questions = []
            question_blocks = txt_content.split('---')
            
            for block in question_blocks:
                block = block.strip()
                if not block:
                    continue
                    
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                
                if len(lines) >= 7:
                    try:
                        q_id = int(lines[0])
                    except:
                        q_id = len(questions) + 1
                    
                    options = lines[2:6]
                    if len(options) < 4:
                        options = options + [''] * (4 - len(options))
                    
                    correct_answer = str(lines[6]).strip()
                    correct_answer = re.sub(r'[^\d]', '', correct_answer)
                    if not correct_answer:
                        correct_answer = '1'
                    
                    question = {
                        'id': q_id,
                        'text': lines[1],
                        'options': options[:4],
                        'correct_option': correct_answer,
                        'solution': lines[7] if len(lines) > 7 else 'समाधान उपलब्ध नहीं'
                    }
                    
                    if question['text'] and len(question['options']) == 4:
                        questions.append(question)
            
            return questions
        except Exception as e:
            raise Exception(f'TXT पार्स करने में त्रुटि: {str(e)}')

    def generate_html(self, questions, test_name, duration, category):
        total_marks = len(questions)
        
        safe_questions = []
        for q in questions:
            safe_questions.append({
                'id': q['id'],
                'text': q['text'],
                'options': q['options'],
                'correct_option': str(q['correct_option']),
                'solution': q.get('solution', 'समाधान उपलब्ध नहीं')
            })
        
        questions_json = json.dumps(safe_questions, ensure_ascii=False)
        
        html_template = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{test_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{max-width:900px;margin:auto;padding:20px;}}
        .welcome-screen {{
            text-align:center;
            background:white;
            padding:40px;
            border-radius:20px;
            box-shadow:0 10px 25px rgba(0,0,0,0.1);
        }}
        .start-btn {{
            background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            color:white;
            border:none;
            padding:15px 40px;
            font-size:1.2rem;
            border-radius:50px;
            cursor:pointer;
        }}
        .quiz-interface, .result-container {{display:none;}}
        .option {{background:#f7fafc;padding:15px;border-radius:10px;margin:10px 0;cursor:pointer;}}
        .option.selected {{background:#667eea;color:white;}}
    </style>
</head>
<body>
    <div class="container">
        <div id="welcome-screen" class="welcome-screen">
            <h1>{test_name}</h1>
            <p>{category}</p>
            <button class="start-btn">Start Quiz</button>
        </div>

        <div id="quiz-interface" class="quiz-interface">
            <div id="question-count"></div>
            <div id="quiz-content"></div>
            <button id="prev-btn" onclick="prevQuestion()">Previous</button>
            <button id="next-btn" onclick="nextQuestion()">Next</button>
            <button id="submit-btn" class="submit-btn" onclick="submitQuiz()">Submit</button>
        </div>

        <div id="result-container" class="result-container">
            <h2>Result</h2>
            <div id="score"></div>
            <button onclick="restartQuiz()">Restart</button>
        </div>
    </div>

    <script>
        const questions = {questions_json};
        let currentQuestionIndex = 0;
        let userAnswers = new Array(questions.length).fill(null);

        function startQuiz() {{
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('quiz-interface').style.display = 'block';
            showQuestion(currentQuestionIndex);
        }}

        function showQuestion(index) {{
            const q = questions[index];
            document.getElementById('question-count').textContent = `Question ${{index + 1}}/${{questions.length}}`;
            let optionsHTML = '';
            q.options.forEach((opt,i)=>{{
                const sel = userAnswers[index]===i+1 ? 'selected':'';
                optionsHTML += `<div class="option ${{sel}}" onclick="selectOption(${{i+1}})">${{opt}}</div>`;
            }});
            document.getElementById('quiz-content').innerHTML = `<h3>${{q.text}}</h3>${{optionsHTML}}`;
        }}

        function selectOption(num) {{
            userAnswers[currentQuestionIndex] = num;
            showQuestion(currentQuestionIndex);
        }}

        function nextQuestion() {{
            if(currentQuestionIndex < questions.length-1) {{
                currentQuestionIndex++;
                showQuestion(currentQuestionIndex);
            }}
        }}

        function prevQuestion() {{
            if(currentQuestionIndex > 0) {{
                currentQuestionIndex--;
                showQuestion(currentQuestionIndex);
            }}
        }}

        function submitQuiz() {{
            let correct=0;
            questions.forEach((q,i)=>{{
                if(userAnswers[i] && userAnswers[i].toString()===q.correct_option) correct++;
            }});
            document.getElementById('quiz-interface').style.display='none';
            document.getElementById('result-container').style.display='block';
            document.getElementById('score').textContent = `Score: ${{correct}}/${{questions.length}}`;
        }}

        function restartQuiz() {{
            currentQuestionIndex=0;
            userAnswers=new Array(questions.length).fill(null);
            document.getElementById('result-container').style.display='none';
            document.getElementById('welcome-screen').style.display='block';
        }}

        // FIX: JS listener for Start button
        document.addEventListener("DOMContentLoaded", ()=>{
            const startBtn=document.querySelector(".start-btn");
            if(startBtn) startBtn.addEventListener("click", startQuiz);
        });
    </script>
</body>
</html>"""
        return html_template


converter = QuizConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        txt_content = data.get('txtContent', '')
        test_name = data.get('testName', 'My Quiz')
        duration = data.get('duration', '60')
        category = data.get('category', 'General Knowledge')

        if not txt_content.strip():
            return jsonify({'success': False, 'error': 'कृपया प्रश्न डालें!'})

        questions = converter.parse_txt_content(txt_content)
        if not questions:
            return jsonify({'success': False, 'error': 'कोई वैध प्रश्न नहीं मिले!'})

        html_output = converter.generate_html(questions, test_name, duration, category)
        return jsonify({'success': True, 'html': html_output, 'questionsCount': len(questions)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
