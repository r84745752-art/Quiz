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
                    
                    # Clean options - take exactly 4 options
                    options = lines[2:6]
                    if len(options) < 4:
                        options = options + [''] * (4 - len(options))
                    
                    # Clean correct answer - only numbers
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
        
        # Create safe questions list
        safe_questions = []
        for q in questions:
            safe_questions.append({
                'id': q['id'],
                'text': q['text'],
                'options': q['options'],
                'correct_option': str(q['correct_option']),
                'solution': q.get('solution', 'समाधान उपलब्ध नहीं')
            })
        
        # Safe JSON serialization
        questions_json = json.dumps(safe_questions, ensure_ascii=False)
        
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
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .welcome-screen {{
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 20px;
        }}
        
        .welcome-title {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .test-name-display {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }}
        
        .category-display {{
            font-size: 1.2rem;
            color: #718096;
            margin-bottom: 20px;
        }}
        
        .quiz-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(240, 147, 251, 0.3);
        }}
        
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .start-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2rem;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }}
        
        .start-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
        }}
        
        .quiz-interface {{
            display: none;
        }}
        
        header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .timer-container {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .timer {{
            display: inline-flex;
            align-items: center;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
        }}
        
        .progress-container {{
            margin: 20px 0;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            height: 10px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }}
        
        .question-count {{
            text-align: right;
            font-size: 1rem;
            color: #4a5568;
            font-weight: 600;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            display: inline-block;
            float: right;
        }}
        
        .question {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 25px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            clear: both;
        }}
        
        .question-text {{
            font-size: 1.3rem;
            font-weight: 500;
            color: #2d3748;
            margin-bottom: 25px;
            line-height: 1.6;
        }}
        
        .options {{
            list-style: none;
        }}
        
        .option {{
            padding: 18px 25px;
            margin-bottom: 15px;
            background: rgba(247, 250, 252, 0.8);
            border: 2px solid rgba(226, 232, 240, 0.5);
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .option:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-color: #667eea;
        }}
        
        .option.selected {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .navigation {{
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
            gap: 15px;
        }}
        
        button {{
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            min-width: 120px;
        }}
        
        button:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }}
        
        button:disabled {{
            background: #b0b0b0 !important;
            cursor: not-allowed;
            transform: none;
            opacity: 0.6;
        }}
        
        #prev-btn {{
            background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
            color: white;
        }}
        
        #next-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .submit-btn {{
            background: linear-gradient(135deg, #1cc88a 0%, #17a673 100%) !important;
            color: white;
            box-shadow: 0 5px 15px rgba(28, 200, 138, 0.4);
        }}
        
        .result-container {{
            display: none;
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .score {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 20px 0;
        }}
        
        .score-breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .breakdown-item {{
            padding: 20px;
            border-radius: 15px;
            color: white;
            font-weight: 600;
        }}
        
        .breakdown-item.correct {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }}
        
        .breakdown-item.incorrect {{
            background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        }}
        
        .breakdown-item.skipped {{
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        }}
        
        .performance-message {{
            font-size: 1.2rem;
            color: #4a5568;
            margin: 20px 0;
            font-weight: 500;
        }}
        
        .detailed-results {{
            text-align: left;
            margin-top: 30px;
        }}
        
        .detailed-results h3 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.4rem;
        }}
        
        .result-question {{
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #667eea;
        }}
        
        .result-question-text {{
            font-weight: 600;
            margin-bottom: 15px;
            color: #2d3748;
        }}
        
        .result-status {{
            float: right;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .status-correct {{
            background: #48bb78;
            color: white;
        }}
        
        .status-incorrect {{
            background: #f56565;
            color: white;
        }}
        
        .status-skipped {{
            background: #ed8936;
            color: white;
        }}
        
        .answer-section {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
        }}
        
        .user-answer {{
            background: #e2e8f0;
            color: #2d3748;
        }}
        
        .correct-answer {{
            background: #c6f6d5;
            color: #22543d;
        }}
        
        .solution {{
            background: #ebf8ff;
            color: #2c5282;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            border-left: 3px solid #3182ce;
        }}
        
        .restart-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }}
        
        .restart-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .welcome-title {{
                font-size: 2rem;
            }}
            
            .navigation {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Welcome Screen -->
        <div class="welcome-screen" id="welcome-screen">
            <h1 class="welcome-title">Welcome to Quiz</h1>
            <h2 class="test-name-display">{test_name}</h2>
            <p class="category-display">{category}</p>
            <div class="quiz-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(questions)}</div>
                    <div class="stat-label">Total Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_marks}</div>
                    <div class="stat-label">Total Marks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{duration}</div>
                    <div class="stat-label">Minutes</div>
                </div>
            </div>
            <button class="start-btn" onclick="startQuiz()">
                <i class="fas fa-play"></i> Start Quiz
            </button>
        </div>

        <!-- Quiz Interface -->
        <div class="quiz-interface" id="quiz-interface">
            <header>
                <h1>{test_name}</h1>
                <p style="text-align: center; color: #718096; margin-top: 5px;">{category}</p>
                <div class="quiz-info">
                    <div class="info-item">Total Questions: {len(questions)}</div>
                    <div class="info-item">Total Marks: {total_marks}</div>
                    <div class="info-item">Time: {duration} Minutes</div>
                </div>
            </header>

            <div class="timer-container">
                <div class="timer" id="timer">
                    <i class="fas fa-clock"></i>
                    <span id="time-display">Loading...</span>
                </div>
            </div>

            <div style="text-align: center; margin: 20px 0;">
                <button class="submit-btn" id="top-submit-btn" onclick="submitQuiz()">
                    <i class="fas fa-check"></i> Submit Quiz
                </button>
            </div>

            <div class="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>

            <div class="question-count" id="question-count">Question 1/{len(questions)}</div>

            <div id="quiz-content">
                <!-- Questions will be loaded here by JavaScript -->
            </div>

            <div class="navigation">
                <button disabled id="prev-btn" onclick="prevQuestion()">
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                <button id="next-btn" onclick="nextQuestion()">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <button class="submit-btn" id="submit-btn" onclick="submitQuiz()" style="display: none;">
                    <i class="fas fa-check"></i> Submit Quiz
                </button>
            </div>
        </div>

        <!-- Results Screen -->
        <div class="result-container" id="result-container">
            <h2>Your Results</h2>
            <div class="score" id="score">0/{total_marks}</div>
            <p class="performance-message" id="result-message"></p>
            <div class="score-breakdown">
                <div class="breakdown-item correct">
                    <div class="breakdown-number" id="correct-count">0</div>
                    <div class="breakdown-label">Correct</div>
                </div>
                <div class="breakdown-item incorrect">
                    <div class="breakdown-number" id="incorrect-count">0</div>
                    <div class="breakdown-label">Incorrect</div>
                </div>
                <div class="breakdown-item skipped">
                    <div class="breakdown-number" id="skipped-count">0</div>
                    <div class="breakdown-label">Skipped</div>
                </div>
            </div>
            <div class="detailed-results">
                <h3>Detailed Results with Solutions</h3>
                <div id="detailed-questions"></div>
            </div>
            <button class="restart-btn" onclick="restartQuiz()">
                <i class="fas fa-redo"></i> Take Quiz Again
            </button>
        </div>
    </div>

    <script>
        // Quiz Data
        const questions = {questions_json};

        // Quiz State
        let currentQuestionIndex = 0;
        let userAnswers = new Array(questions.length).fill(null);
        let timer;
        let timeLeft = {int(duration) * 60};

        function startQuiz() {{
            console.log('Starting quiz...');
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('quiz-interface').style.display = 'block';
            document.getElementById('result-container').style.display = 'none';
            startTimer();
            showQuestion(currentQuestionIndex);
        }}

        function startTimer() {{
            timer = setInterval(function() {{
                timeLeft--;
                updateTimerDisplay();
                if (timeLeft <= 0) {{
                    clearInterval(timer);
                    submitQuiz();
                }}
            }}, 1000);
        }}

        function updateTimerDisplay() {{
            const hours = Math.floor(timeLeft / 3600);
            const minutes = Math.floor((timeLeft % 3600) / 60);
            const seconds = timeLeft % 60;
            document.getElementById('time-display').textContent = 
                `${{hours.toString().padStart(2, '0')}}:${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
        }}

        function showQuestion(index) {{
            const question = questions[index];
            const progress = ((index + 1) / questions.length) * 100;
            
            document.getElementById('progress-bar').style.width = `${{progress}}%`;
            document.getElementById('question-count').textContent = `Question ${{index + 1}}/${{questions.length}}`;

            let optionsHtml = '';
            question.options.forEach((option, i) => {{
                const optionNumber = i + 1;
                const isSelected = userAnswers[index] === optionNumber;
                optionsHtml += `<li class="option ${{isSelected ? 'selected' : ''}}" onclick="selectOption(${{optionNumber}})">${{option}}</li>`;
            }});

            document.getElementById('quiz-content').innerHTML = `
                <div class="question">
                    <div class="question-text">${{question.text}}</div>
                    <ul class="options">${{optionsHtml}}</ul>
                </div>
            `;

            document.getElementById('prev-btn').disabled = index === 0;
            
            if (index === questions.length - 1) {{
                document.getElementById('next-btn').style.display = 'none';
                document.getElementById('submit-btn').style.display = 'inline-block';
            }} else {{
                document.getElementById('next-btn').style.display = 'inline-block';
                document.getElementById('submit-btn').style.display = 'none';
            }}
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
            calculateResults();
            document.getElementById('quiz-interface').style.display = 'none';
            document.getElementById('result-container').style.display = 'block';
        }}

        function calculateResults() {{
            let correctCount = 0;
            let incorrectCount = 0;
            let skippedCount = 0;

            questions.forEach((question, index) => {{
                const userAnswer = userAnswers[index];
                if (userAnswer === null) {{
                    skippedCount++;
                }} else if (userAnswer.toString() === question.correct_option) {{
                    correctCount++;
                }} else {{
                    incorrectCount++;
                }}
            }});

            const score = correctCount;
            const totalQuestions = questions.length;

            document.getElementById('score').textContent = `${{score}}/${{totalQuestions}}`;
            document.getElementById('correct-count').textContent = correctCount;
            document.getElementById('incorrect-count').textContent = incorrectCount;
            document.getElementById('skipped-count').textContent = skippedCount;

            const percentage = (score / totalQuestions) * 100;
            let message = '';
            if (percentage >= 80) {{
                message = 'Excellent performance! 🎉';
            }} else if (percentage >= 60) {{
                message = 'Good job! 👍';
            }} else if (percentage >= 40) {{
                message = 'Average performance. Keep practicing! 💪';
            }} else {{
                message = 'Need more practice. Don\\\\'t give up! 📚';
            }}
            document.getElementById('result-message').textContent = message;

            showDetailedResults();
        }}

        function showDetailedResults() {{
            const detailedQuestions = document.getElementById('detailed-questions');
            let detailedHtml = '';

            questions.forEach((question, index) => {{
                const userAnswer = userAnswers[index];
                const isCorrect = userAnswer !== null && userAnswer.toString() === question.correct_option;
                const isSkipped = userAnswer === null;
                
                let statusClass = '';
                let statusText = '';
                
                if (isSkipped) {{
                    statusClass = 'status-skipped';
                    statusText = 'Skipped';
                }} else if (isCorrect) {{
                    statusClass = 'status-correct';
                    statusText = 'Correct';
                }} else {{
                    statusClass = 'status-incorrect';
                    statusText = 'Incorrect';
                }}

                detailedHtml += `
                    <div class="result-question">
                        <div class="result-question-text">
                            ${{index + 1}}. ${{question.text}}
                            <span class="result-status ${{statusClass}}">${{statusText}}</span>
                        </div>
                        <div class="answer-section user-answer">
                            <strong>Your Answer:</strong> 
                            ${{userAnswer !== null ? question.options[userAnswer - 1] : 'Not attempted'}}
                        </div>
                        <div class="answer-section correct-answer">
                            <strong>Correct Answer:</strong> 
                            ${{question.options[parseInt(question.correct_option) - 1]}}
                        </div>
                        <div class="solution">
                            <strong>Solution:</strong> ${{question.solution}}
                        </div>
                    </div>
                `;
            }});

            detailedQuestions.innerHTML = detailedHtml;
        }}

        function restartQuiz() {{
            currentQuestionIndex = 0;
            userAnswers = new Array(questions.length).fill(null);
            timeLeft = {int(duration) * 60};
            
            document.getElementById('result-container').style.display = 'none';
            document.getElementById('welcome-screen').style.display = 'block';
            document.getElementById('next-btn').style.display = 'inline-block';
            document.getElementById('submit-btn').style.display = 'none';
            document.getElementById('progress-bar').style.width = '0%';
        }}

        // Initialize timer display
        updateTimerDisplay();
        
        // Debug info
        console.log('Quiz loaded with', questions.length, 'questions');
        console.log('Questions data:', questions);
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