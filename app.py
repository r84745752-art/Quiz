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
        
        # Complete HTML template with detailed results
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
            color: #333;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .welcome-screen {{
            text-align: center;
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
        
        .telegram-btn {{
            display: inline-block;
            padding: 12px 25px;
            background: linear-gradient(135deg, #0088cc, #005f99);
            color: white;
            border-radius: 25px;
            font-weight: 600;
            text-decoration: none;
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
            margin-top: 20px;
        }}
        
        .start-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
        }}
        
        /* Quiz Interface */
        .quiz-interface {{
            display: none;
        }}
        
        .quiz-header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .quiz-title {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }}
        
        .quiz-info {{
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .info-item {{
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 12px 20px;
            border-radius: 25px;
            margin: 5px;
            font-weight: 600;
            border: 1px solid rgba(102, 126, 234, 0.2);
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
        
        .timer i {{
            margin-right: 8px;
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
            position: relative;
            overflow: hidden;
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
        
        .option.correct {{
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
            color: white !important;
            border-color: #48bb78 !important;
        }}
        
        .option.incorrect {{
            background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%) !important;
            color: white !important;
            border-color: #f56565 !important;
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
        
        /* Results Section */
        .result-container {{
            display: none;
            text-align: center;
            padding: 40px;
        }}
        
        .result-container h2 {{
            font-size: 2rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 20px;
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
            text-align: left;
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
        
        .breakdown-number {{
            font-size: 1.5rem;
            margin-bottom: 5px;
        }}
        
        .breakdown-label {{
            font-size: 0.9rem;
            opacity: 0.9;
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
            text-align: left;
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
            
            .test-name-display {{
                font-size: 1.4rem;
            }}
            
            .quiz-info {{
                flex-direction: column;
                align-items: center;
            }}
            
            .navigation {{
                flex-direction: column;
            }}
            
            .score-breakdown {{
                grid-template-columns: 1fr;
            }}
            
            .question {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Welcome Screen -->
        <div class="card welcome-screen" id="welcome-screen">
            <h1 class="welcome-title">Welcome to Quiz</h1>
            <h2 class="test-name-display">{test_name}</h2>
            <p class="category-display">{category}</p>
            <a href="https://t.me/DecodeSikar" class="telegram-btn" target="_blank">
                🚀 Join Telegram
            </a>
            <div class="quiz-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(questions)}</div>
                    <div class="stat-label">Total Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(questions)}</div>
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
        <div class="card quiz-interface" id="quiz-interface">
            <div class="quiz-header">
                <h1 class="quiz-title">{test_name}</h1>
                <p style="text-align: center; color: #718096; margin-top: 5px;">{category}</p>
                <div class="quiz-info">
                    <div class="info-item">Total Questions: {len(questions)}</div>
                    <div class="info-item">Total Marks: {len(questions)}</div>
                    <div class="info-item">Time: {duration} Minutes</div>
                </div>
            </div>
            
            <div class="timer-container">
                <div class="timer" id="timer">
                    <i class="fas fa-clock"></i>
                    <span id="time-display">Loading...</span>
                </div>
            </div>
            
            <!-- Top Submit Button -->
            <div style="text-align: center; margin: 20px 0;">
                <button class="submit-btn" id="top-submit-btn" onclick="submitQuiz()" style="display: none;">
                    <i class="fas fa-check"></i> Submit Quiz
                </button>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            
            <div class="question-count" id="question-count">Question 1/{len(questions)}</div>
            
            <div id="quiz-content">
                <!-- Questions will be inserted here by JavaScript -->
            </div>
            
            <div class="navigation">
                <button disabled id="prev-btn" onclick="prevQuestion()">
                    <i class="fas fa-chevron-left"></i> Previous / पिछला
                </button>
                <button id="next-btn" onclick="nextQuestion()">
                    Next / अगला <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="submit-btn" id="submit-btn" onclick="submitQuiz()" style="display: none;">
                    <i class="fas fa-check"></i> Submit Quiz / परीक्षा समाप्त करें
                </button>
            </div>
        </div>

        <!-- Results -->
        <div class="card result-container" id="result-container">
            <h2>Your Results</h2>
            <div class="score" id="score">0/{len(questions)}</div>
            <p class="performance-message" id="result-message"></p>
            <div class="score-breakdown" id="score-breakdown">
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
            <div class="detailed-results" id="detailed-results">
                <h3>Detailed Results with Solutions</h3>
                <div id="detailed-questions"></div>
            </div>
            <button class="restart-btn" onclick="restartQuiz()">
                <i class="fas fa-redo"></i> Take Quiz Again
            </button>
        </div>
    </div>

    <script>
        const questions = {questions_json};
        const examInfo = {{
            "test_duration": "{duration}",
            "test_total_question": {len(questions)},
            "test_total_marks": {len(questions)}
        }};

        // Quiz state variables
        let currentQuestionIndex = 0;
        let userAnswers = new Array(questions.length).fill(null);
        let timer;
        let timeLeft = parseInt(examInfo.test_duration) * 60;
        let quizStarted = false;

        // Start the quiz
        function startQuiz() {{
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('quiz-interface').style.display = 'block';
            quizStarted = true;
            startTimer();
            showQuestion(currentQuestionIndex);
            updateProgressBar();
            updateNavigationButtons();
        }}

        // Timer functions
        function startTimer() {{
            updateTimerDisplay();
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

        // Question navigation
        function showQuestion(index) {{
            const quizContent = document.getElementById('quiz-content');
            const question = questions[index];
            
            document.getElementById('question-count').textContent = `Question ${{index + 1}}/${{questions.length}}`;
            
            let optionsHtml = '';
            question.options.forEach((option, optionIndex) => {{
                const isSelected = userAnswers[index] === (optionIndex + 1).toString();
                const optionClass = isSelected ? 'option selected' : 'option';
                optionsHtml += `
                    <li class="${{optionClass}}" onclick="selectOption(${{optionIndex + 1}})">
                        ${{option}}
                    </li>
                `;
            }});

            quizContent.innerHTML = `
                <div class="question">
                    <div class="question-text">${{question.text}}</div>
                    <ul class="options">${{optionsHtml}}</ul>
                </div>
            `;

            updateNavigationButtons();
            updateProgressBar();
        }}

        function selectOption(optionNumber) {{
            userAnswers[currentQuestionIndex] = optionNumber.toString();
            showQuestion(currentQuestionIndex);
            updateSubmitButton();
        }}

        function prevQuestion() {{
            if (currentQuestionIndex > 0) {{
                currentQuestionIndex--;
                showQuestion(currentQuestionIndex);
            }}
        }}

        function nextQuestion() {{
            if (currentQuestionIndex < questions.length - 1) {{
                currentQuestionIndex++;
                showQuestion(currentQuestionIndex);
            }}
            updateSubmitButton();
        }}

        function updateNavigationButtons() {{
            document.getElementById('prev-btn').disabled = currentQuestionIndex === 0;
            document.getElementById('next-btn').disabled = currentQuestionIndex === questions.length - 1;
        }}

        function updateSubmitButton() {{
            const answeredQuestions = userAnswers.filter(answer => answer !== null).length;
            const submitBtn = document.getElementById('submit-btn');
            const topSubmitBtn = document.getElementById('top-submit-btn');
            
            if (answeredQuestions >= questions.length * 0.5) {{
                submitBtn.style.display = 'inline-block';
                topSubmitBtn.style.display = 'inline-block';
            }}
        }}

        function updateProgressBar() {{
            const answeredQuestions = userAnswers.filter(answer => answer !== null).length;
            const progress = (answeredQuestions / questions.length) * 100;
            document.getElementById('progress-bar').style.width = `${{progress}}%`;
        }}

        // Quiz submission and results
        function submitQuiz() {{
            if (quizStarted) {{
                clearInterval(timer);
                document.getElementById('quiz-interface').style.display = 'none';
                document.getElementById('result-container').style.display = 'block';
                showResults();
            }}
        }}

        function showResults() {{
            let correctCount = 0;
            let incorrectCount = 0;
            let skippedCount = 0;

            questions.forEach((question, index) => {{
                if (userAnswers[index] === null) {{
                    skippedCount++;
                }} else if (userAnswers[index] === question.correct_option) {{
                    correctCount++;
                }} else {{
                    incorrectCount++;
                }}
            }});

            const score = correctCount;
            const percentage = (correctCount / questions.length) * 100;

            document.getElementById('score').textContent = `${{score}}/${{questions.length}}`;
            document.getElementById('correct-count').textContent = correctCount;
            document.getElementById('incorrect-count').textContent = incorrectCount;
            document.getElementById('skipped-count').textContent = skippedCount;

            let message = '';
            if (percentage >= 80) {{
                message = 'Excellent! You have a great understanding of Agriculture Science.';
            }} else if (percentage >= 60) {{
                message = 'Good job! You have a solid foundation in Agriculture Science.';
            }} else if (percentage >= 40) {{
                message = 'Not bad! Keep practicing to improve your knowledge.';
            }} else {{
                message = 'Keep studying! You will do better next time.';
            }}
            document.getElementById('result-message').textContent = message;

            showDetailedResults();
        }}

        function showDetailedResults() {{
            const detailedQuestions = document.getElementById('detailed-questions');
            let detailedHtml = '';

            questions.forEach((question, index) => {{
                const userAnswer = userAnswers[index];
                const isCorrect = userAnswer === question.correct_option;
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
                            ${{isSkipped ? 'Not attempted' : (question.options[parseInt(userAnswer) - 1] || 'Invalid answer')}}
                        </div>
                        ${{!isCorrect && !isSkipped ? `
                            <div class="answer-section correct-answer">
                                <strong>Correct Answer:</strong> ${{question.options[parseInt(question.correct_option) - 1]}}
                            </div>
                        ` : ''}}
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
            timeLeft = parseInt(examInfo.test_duration) * 60;
            quizStarted = false;

            document.getElementById('result-container').style.display = 'none';
            document.getElementById('welcome-screen').style.display = 'block';
            
            document.getElementById('submit-btn').style.display = 'none';
            document.getElementById('top-submit-btn').style.display = 'none';
            
            updateProgressBar();
        }}

        // Initialize quiz
        document.getElementById('question-count').textContent = `Question 1/${{questions.length}}`;
        updateProgressBar();
    </script>
</body>
</html>'''
        return html_template

converter = QuizConverter()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quiz Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            textarea { width: 100%; height: 300px; margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Quiz Generator</h1>
        <form id="quizForm">
            <div>
                <label>Test Name:</label>
                <input type="text" name="testName" value="VDO Test - 08 (Agriculture Science)" required>
            </div>
            <div>
                <label>Duration (minutes):</label>
                <input type="number" name="duration" value="120" required>
            </div>
            <div>
                <label>Category:</label>
                <input type="text" name="category" value="VDO-2025" required>
            </div>
            <div>
                <label>Questions (TXT format):</label>
                <textarea name="txtContent" placeholder="Paste your questions in TXT format here..." required></textarea>
            </div>
            <button type="submit">Generate Quiz</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('quizForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        // Open quiz in new window
                        const newWindow = window.open('', '_blank');
                        newWindow.document.write(result.html);
                        newWindow.document.close();
                    } else {
                        document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    '''

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