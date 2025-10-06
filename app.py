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
                
                # Minimum 6 lines required: ID, Question, 4 options, correct answer
                if len(lines) >= 6:
                    try:
                        q_id = int(lines[0])
                    except:
                        q_id = len(questions) + 1
                    
                    # Clean options - remove any extra text
                    options = []
                    for i in range(2, 6):
                        if i < len(lines):
                            # Remove "Answer Option Number:" etc. from options
                            option_text = lines[i].replace('Answer Option Number:', '').replace('उत्तर:', '').strip()
                            options.append(option_text)
                    
                    # Clean correct answer - should be just number
                    correct_answer = str(lines[6]).strip()
                    correct_answer = re.sub(r'[^\d]', '', correct_answer)  # Keep only digits
                    if not correct_answer and len(lines) > 6:
                        correct_answer = '1'  # Default to first option
                    
                    question = {
                        'id': q_id,
                        'text': lines[1],
                        'options': options[:4],  # Ensure exactly 4 options
                        'correct_option': correct_answer,
                        'solution': lines[7] if len(lines) > 7 else 'समाधान उपलब्ध नहीं'
                    }
                    
                    # Validate question has proper data
                    if (question['text'] and 
                        len(question['options']) == 4 and 
                        question['correct_option']):
                        questions.append(question)
            
            return questions
        except Exception as e:
            raise Exception(f'TXT पार्स करने में त्रुटि: {str(e)}')

    def generate_html(self, questions, test_name, duration, category):
        total_marks = len(questions)
        
        # Safe JSON serialization with validation
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
        
        # Simple and clean HTML template
        html_template = f'''<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{test_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .welcome-screen {{
            padding: 40px;
            text-align: center;
        }}
        
        .welcome-title {{
            font-size: 2rem;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .quiz-stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            min-width: 120px;
        }}
        
        .start-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            border-radius: 25px;
            cursor: pointer;
            margin-top: 20px;
        }}
        
        .quiz-interface {{
            display: none;
            padding: 20px;
        }}
        
        .timer {{
            background: #ff6b6b;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
        }}
        
        .question {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .options {{
            list-style: none;
            margin-top: 20px;
        }}
        
        .option {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .option:hover {{
            border-color: #667eea;
            transform: translateY(-2px);
        }}
        
        .option.selected {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .navigation {{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }}
        
        .nav-btn {{
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }}
        
        #prev-btn {{
            background: #6c757d;
            color: white;
        }}
        
        #next-btn {{
            background: #667eea;
            color: white;
        }}
        
        .submit-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            margin-top: 20px;
        }}
        
        .result-container {{
            display: none;
            padding: 40px;
            text-align: center;
        }}
        
        .score {{
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="welcome-screen" id="welcome-screen">
            <h1 class="welcome-title">Welcome to Quiz</h1>
            <h2>{test_name}</h2>
            <p>{category}</p>
            <div class="quiz-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(questions)}</div>
                    <div>Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{duration}</div>
                    <div>Minutes</div>
                </div>
            </div>
            <button class="start-btn" onclick="startQuiz()">
                <i class="fas fa-play"></i> Start Quiz
            </button>
        </div>

        <div class="quiz-interface" id="quiz-interface">
            <div class="timer" id="timer">60:00</div>
            
            <div id="quiz-content">
                <!-- Questions will be loaded here -->
            </div>
            
            <div class="navigation">
                <button class="nav-btn" id="prev-btn" onclick="prevQuestion()" disabled>
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                <button class="nav-btn" id="next-btn" onclick="nextQuestion()">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            
            <button class="submit-btn" id="submit-btn" onclick="submitQuiz()" style="display: none;">
                Submit Quiz
            </button>
        </div>

        <div class="result-container" id="result-container">
            <h2>Quiz Completed!</h2>
            <div class="score" id="score">0/{len(questions)}</div>
            <button class="start-btn" onclick="restartQuiz()">
                <i class="fas fa-redo"></i> Try Again
            </button>
        </div>
    </div>

    <script>
        const questions = {questions_json};
        let currentQuestionIndex = 0;
        let userAnswers = new Array(questions.length).fill(null);
        let timeLeft = {int(duration) * 60};
        let timer;

        function startQuiz() {{
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('quiz-interface').style.display = 'block';
            startTimer();
            showQuestion(currentQuestionIndex);
        }}

        function startTimer() {{
            timer = setInterval(() => {{
                timeLeft--;
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                document.getElementById('timer').textContent = 
                    `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
                
                if (timeLeft <= 0) {{
                    clearInterval(timer);
                    submitQuiz();
                }}
            }}, 1000);
        }}

        function showQuestion(index) {{
            const question = questions[index];
            let optionsHtml = '';
            
            question.options.forEach((option, i) => {{
                const isSelected = userAnswers[index] === (i + 1);
                optionsHtml += `
                    <li class="option ${{isSelected ? 'selected' : ''}}" 
                        onclick="selectOption(${{i + 1}})">
                        ${{option}}
                    </li>
                `;
            }});
            
            document.getElementById('quiz-content').innerHTML = `
                <div class="question">
                    <h3>${{question.text}}</h3>
                    <ul class="options">${{optionsHtml}}</ul>
                </div>
            `;
            
            // Update navigation
            document.getElementById('prev-btn').disabled = index === 0;
            document.getElementById('next-btn').style.display = 
                index === questions.length - 1 ? 'none' : 'block';
            document.getElementById('submit-btn').style.display = 
                index === questions.length - 1 ? 'block' : 'none';
        }}

        function selectOption(optionNumber) {{
            userAnswers[currentQuestionIndex] = optionNumber;
            showQuestion(currentQuestionIndex);
        }}

        function nextQuestion() {{
            if (currentQuestionIndex < questions.length - 1) {{
                currentQuestionIndex++;
                showQuestion(currentQuestionIndex);
            }}
        }}

        function prevQuestion() {{
            if (currentQuestionIndex > 0) {{
                currentQuestionIndex--;
                showQuestion(currentQuestionIndex);
            }}
        }}

        function submitQuiz() {{
            clearInterval(timer);
            let correctCount = 0;
            
            questions.forEach((question, index) => {{
                if (userAnswers[index] && userAnswers[index].toString() === question.correct_option) {{
                    correctCount++;
                }}
            }});
            
            document.getElementById('score').textContent = `${{correctCount}}/${{questions.length}}`;
            document.getElementById('quiz-interface').style.display = 'none';
            document.getElementById('result-container').style.display = 'block';
        }}

        function restartQuiz() {{
            currentQuestionIndex = 0;
            userAnswers = new Array(questions.length).fill(null);
            timeLeft = {int(duration) * 60};
            document.getElementById('result-container').style.display = 'none';
            document.getElementById('welcome-screen').style.display = 'block';
        }}
    </script>
</body>
</html>'''
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
            return jsonify({
                'success': False,
                'error': 'कृपया प्रश्न डालें!'
            })

        questions = converter.parse_txt_content(txt_content)
        
        if not questions:
            return jsonify({
                'success': False,
                'error': 'कोई वैध प्रश्न नहीं मिले! कृपया format check करें।'
            })

        html_output = converter.generate_html(questions, test_name, duration, category)
        
        return jsonify({
            'success': True,
            'html': html_output,
            'questionsCount': len(questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)