"""
Django management command to generate mock LMS data
Usage: python manage.py generate_lms_mock_data --schema=kk_company
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import connection
from django.core.files import File
from training.models import (
    Course, CourseModule, Lesson, CourseEnrollment, Instructor, CourseMaterial
)
from hr.models import Employee
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate mock LMS data for testing and demonstration (use --schema=tenant_name)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing LMS data before generating new data',
        )
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name (e.g., kk_company)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('LMS Mock Data Generator'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')

        # Set schema if provided
        schema_name = options.get('schema')
        if schema_name:
            self.stdout.write(f'Setting schema to: {schema_name}')
            connection.set_schema(schema_name)
            self.stdout.write(self.style.SUCCESS(f'[OK] Using schema: {schema_name}'))
            self.stdout.write('')
        else:
            current_schema = connection.schema_name
            self.stdout.write(f'Current schema: {current_schema}')
            if current_schema == 'public':
                self.stdout.write(self.style.WARNING('[WARNING] You are in the public schema!'))
                self.stdout.write(self.style.WARNING('   Use --schema=kk_company (or your tenant name)'))
                self.stdout.write('')
                self.stdout.write('Available schemas:')
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT schema_name FROM information_schema.schemata
                    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast', 'public')
                    ORDER BY schema_name
                """)
                schemas = cursor.fetchall()
                for schema in schemas:
                    self.stdout.write(f'  - {schema[0]}')
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('Please run with --schema=<tenant_name>'))
                return
            self.stdout.write(self.style.SUCCESS(f'[OK] Using schema: {current_schema}'))
            self.stdout.write('')

        # Clear existing data if requested
        if options['clear']:
            self.stdout.write(self.style.WARNING('[WARNING] Clearing existing LMS data...'))
            Course.objects.all().delete()
            Instructor.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('[OK] Existing data cleared'))
            self.stdout.write('')

        try:
            # Get or create instructor (optional - courses can exist without instructor)
            self.stdout.write('Setting up instructor profile...')
            instructor = None
            staff_user = User.objects.filter(is_staff=True).first()

            if not staff_user:
                self.stdout.write(self.style.WARNING('[WARNING] No staff user found'))
                self.stdout.write(self.style.WARNING('  Courses will be created without instructor'))
            else:
                try:
                    # Try to get employee profile
                    employee = staff_user.employee
                    instructor, created = Instructor.objects.get_or_create(
                        user=staff_user,
                        defaults={
                            'bio': 'Experienced instructor with expertise in leadership, technical training, and professional development. Passionate about helping employees reach their full potential.',
                            'expertise': 'Leadership, Communication, Technical Training, Soft Skills Development',
                            'is_active': True
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'[OK] Created instructor: {staff_user.get_full_name()}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'[OK] Using existing instructor: {staff_user.get_full_name()}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'[WARNING] Could not create instructor: {str(e)}'))
                    self.stdout.write(self.style.WARNING('  Courses will be created without instructor'))
                    instructor = None

            self.stdout.write('')

            # Course 1: Leadership and Communication
            self.stdout.write('Creating Course 1: Leadership and Communication Essentials...')
            course1, created = Course.objects.update_or_create(
                code='LEAD-101',
                defaults={
                    'title': 'Leadership and Communication Essentials',
                    'description': '''Master the fundamental skills of effective leadership and communication.

This comprehensive course covers everything from self-awareness and emotional intelligence to team management and strategic communication. Learn practical techniques that you can apply immediately in your workplace.

Throughout this course, you'll develop:
• Core leadership competencies and styles
• Effective communication strategies for different audiences
• Conflict resolution and negotiation skills
• Team building and motivation techniques
• Decision-making and problem-solving frameworks

Perfect for aspiring leaders, new managers, and anyone looking to enhance their leadership capabilities.''',
                    'category': 'leadership',
                    'level': 'intermediate',
                    'instructor': instructor,
                    'duration_hours': 24,
                    'max_students': 30,
                    'passing_score': 75,
                    'status': 'published',
                    'is_mandatory': False
                }
            )
            course1.modules.all().delete()

            # Module 1-1
            module1_1 = CourseModule.objects.create(
                course=course1,
                title='Introduction to Leadership',
                description='Understand the fundamentals of leadership and discover your leadership style.',
                order=1
            )

            Lesson.objects.create(
                module=module1_1,
                title='What is Leadership?',
                content_type='text',
                duration_minutes=30,
                description='Explore the definition and core concepts of leadership',
                content='''<h2>Understanding Leadership</h2>
<p>Leadership is the art of motivating a group of people to act toward achieving a common goal. In a business setting, this can mean directing workers and colleagues with a strategy to meet the company's needs.</p>

<h3>Key Characteristics of Effective Leaders:</h3>
<ul>
<li><strong>Vision:</strong> The ability to see the big picture and set clear goals</li>
<li><strong>Communication:</strong> Articulating ideas clearly and listening actively</li>
<li><strong>Integrity:</strong> Being honest, ethical, and consistent</li>
<li><strong>Empathy:</strong> Understanding and relating to others' perspectives</li>
<li><strong>Decisiveness:</strong> Making timely and well-considered decisions</li>
<li><strong>Adaptability:</strong> Adjusting to changing circumstances</li>
</ul>

<h3>Leadership vs Management</h3>
<p>While often used interchangeably, leadership and management are distinct:</p>
<ul>
<li><strong>Leadership</strong> is about inspiring and influencing others toward a vision</li>
<li><strong>Management</strong> is about planning, organizing, and controlling resources</li>
</ul>''',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module1_1,
                title='Leadership Styles and Approaches',
                content_type='video',
                duration_minutes=45,
                description='Discover different leadership styles and when to use them',
                content='''<h2>Leadership Styles</h2>
<p>Watch this video to learn about different leadership approaches and when to apply them.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/eUGXsKY8YZM"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Common Leadership Styles:</h3>

<h4>1. Transformational Leadership</h4>
<p>Inspires and motivates followers to exceed expectations and develop their own leadership capacity.</p>
<ul>
<li>Best for: Innovation and major organizational change</li>
<li>Characteristics: Visionary, inspiring, development-focused</li>
</ul>

<h4>2. Servant Leadership</h4>
<p>Focuses on serving others and prioritizing their needs.</p>
<ul>
<li>Best for: Building trust and long-term relationships</li>
<li>Characteristics: Empathetic, community-oriented, supportive</li>
</ul>

<h4>3. Democratic Leadership</h4>
<p>Involves team members in decision-making processes.</p>
<ul>
<li>Best for: Creative problem-solving and team buy-in</li>
<li>Characteristics: Collaborative, inclusive, consultative</li>
</ul>

<h4>4. Situational Leadership</h4>
<p>Adapts leadership style based on the situation and team maturity.</p>
<ul>
<li>Best for: Diverse teams with varying skill levels</li>
<li>Characteristics: Flexible, adaptive, assessment-driven</li>
</ul>''',
                video_url='https://www.youtube.com/watch?v=eUGXsKY8YZM',
                order=2,
                is_mandatory=True
            )

            lesson1_3 = Lesson.objects.create(
                module=module1_1,
                title='Self-Assessment: Discover Your Leadership Style',
                content_type='document',
                duration_minutes=25,
                description='Download and complete the leadership style assessment',
                content='''<h2>Leadership Self-Assessment</h2>
<p>Complete this assessment to identify your natural leadership tendencies.</p>

<div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
    <p><strong>📄 Assessment Document:</strong></p>
    <p>Download the Leadership Style Self-Assessment worksheet below (in Training Materials section) to complete this activity.</p>
</div>

<h3>Instructions:</h3>
<ol>
<li>Download the assessment worksheet</li>
<li>Answer all questions honestly based on your typical behavior</li>
<li>Calculate your scores for each leadership style</li>
<li>Review your results and reflection questions</li>
<li>Consider how you can develop areas for growth</li>
</ol>

<h3>What You'll Discover:</h3>
<ul>
<li>Your dominant leadership style</li>
<li>Secondary leadership tendencies</li>
<li>Strengths and areas for development</li>
<li>Situations where you're most effective</li>
<li>Strategies to expand your leadership repertoire</li>
</ul>

<p><em>Note: Upload your completed assessment if your instructor requires submission.</em></p>''',
                order=3,
                is_mandatory=True
            )

            # Module 1-2
            module1_2 = CourseModule.objects.create(
                course=course1,
                title='Communication Fundamentals',
                description='Master the essential skills of effective communication in professional settings.',
                order=2
            )

            Lesson.objects.create(
                module=module1_2,
                title='Principles of Effective Communication',
                content_type='text',
                duration_minutes=35,
                description='Learn the core principles that make communication effective',
                content='''<h2>The Foundation of Effective Communication</h2>
<p>Communication is the lifeblood of any organization. Effective communication ensures that information flows smoothly, relationships strengthen, and goals are achieved.</p>

<h3>The Communication Process</h3>
<ol>
<li><strong>Sender:</strong> The person initiating the message</li>
<li><strong>Encoding:</strong> Converting thoughts into words/symbols</li>
<li><strong>Channel:</strong> The medium through which the message travels</li>
<li><strong>Receiver:</strong> The person receiving the message</li>
<li><strong>Decoding:</strong> Interpreting the message</li>
<li><strong>Feedback:</strong> Response from the receiver</li>
</ol>

<h3>Barriers to Effective Communication</h3>
<ul>
<li><strong>Physical barriers:</strong> Noise, distance, technical issues</li>
<li><strong>Psychological barriers:</strong> Stress, emotions, attitudes</li>
<li><strong>Language barriers:</strong> Jargon, technical terms, different languages</li>
<li><strong>Cultural barriers:</strong> Different norms and expectations</li>
</ul>''',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module1_2,
                title='Active Listening Skills',
                content_type='video',
                duration_minutes=40,
                description='Develop your ability to truly hear and understand others',
                content='''<h2>The Power of Active Listening</h2>
<p>Watch this video to learn the essential components of active listening.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/t1NorADqZyY"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Components of Active Listening</h3>

<h4>1. Paying Attention</h4>
<ul>
<li>Give the speaker your full attention</li>
<li>Put away distractions (phone, computer, etc.)</li>
<li>Make appropriate eye contact</li>
<li>Observe non-verbal cues</li>
</ul>

<h4>2. Showing That You're Listening</h4>
<ul>
<li>Use body language (nodding, leaning forward)</li>
<li>Provide verbal affirmations ("I see", "Go on")</li>
<li>Maintain an open posture</li>
</ul>

<h4>3. Providing Feedback</h4>
<ul>
<li>Ask clarifying questions</li>
<li>Paraphrase to confirm understanding</li>
<li>Summarize key points</li>
</ul>

<h4>4. Deferring Judgment</h4>
<ul>
<li>Listen without forming immediate opinions</li>
<li>Allow the speaker to finish completely</li>
<li>Consider their perspective before responding</li>
</ul>''',
                video_url='https://www.youtube.com/watch?v=t1NorADqZyY',
                order=2,
                is_mandatory=True
            )

            lesson1_6 = Lesson.objects.create(
                module=module1_2,
                title='Non-Verbal Communication Guide',
                content_type='document',
                duration_minutes=30,
                description='Understanding body language and non-verbal cues',
                content='''<h2>The Silent Language</h2>
<p>Research shows that 55% of communication is through body language, 38% through tone of voice, and only 7% through words.</p>

<div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
    <p><strong>📚 Reading Material:</strong></p>
    <p>Check the Training Materials section below for the comprehensive Non-Verbal Communication Guide PDF.</p>
</div>

<h3>Key Areas of Non-Verbal Communication:</h3>

<h4>Facial Expressions</h4>
<ul>
<li>Universal emotions: happiness, sadness, anger, surprise, fear, disgust</li>
<li>Microexpressions reveal true feelings</li>
<li>Smiling conveys warmth and approachability</li>
</ul>

<h4>Body Language & Posture</h4>
<ul>
<li>Open posture shows confidence and receptiveness</li>
<li>Closed posture may indicate defensiveness</li>
<li>Leaning forward shows interest</li>
</ul>

<h4>Eye Contact</h4>
<ul>
<li>Shows attention and builds trust</li>
<li>Too much can be intimidating</li>
<li>Too little may seem disinterested</li>
</ul>

<h4>Personal Space</h4>
<ul>
<li>Intimate: 0-18 inches</li>
<li>Personal: 18 inches - 4 feet</li>
<li>Social: 4-12 feet</li>
<li>Public: 12+ feet</li>
</ul>''',
                order=3,
                is_mandatory=True
            )

            # Module 1-3: Team Building
            module1_3 = CourseModule.objects.create(
                course=course1,
                title='Building High-Performance Teams',
                description='Learn strategies for building and leading effective teams.',
                order=3
            )

            Lesson.objects.create(
                module=module1_3,
                title='Team Development Stages',
                content_type='video',
                duration_minutes=35,
                description='Understanding how teams form and develop over time',
                content='''<h2>The Five Stages of Team Development</h2>
<p>Watch this video to understand how teams evolve through different stages.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/OhSI6oBQmQA"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Tuckman's Model:</h3>

<h4>1. Forming</h4>
<ul>
<li>Team members are polite and positive</li>
<li>Roles and responsibilities are unclear</li>
<li>Leader provides direction and structure</li>
</ul>

<h4>2. Storming</h4>
<ul>
<li>Conflicts emerge as personalities clash</li>
<li>Competition for position and influence</li>
<li>Leader facilitates resolution</li>
</ul>

<h4>3. Norming</h4>
<ul>
<li>Team establishes working norms</li>
<li>Roles become clearer</li>
<li>Trust and cooperation increase</li>
</ul>

<h4>4. Performing</h4>
<ul>
<li>Team works efficiently toward goals</li>
<li>Strong sense of unity</li>
<li>High productivity and effectiveness</li>
</ul>

<h4>5. Adjourning</h4>
<ul>
<li>Project completion or team disbands</li>
<li>Recognize achievements</li>
<li>Reflect on learnings</li>
</ul>''',
                video_url='https://www.youtube.com/watch?v=OhSI6oBQmQA',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module1_3,
                title='Conflict Resolution in Teams',
                content_type='video',
                duration_minutes=40,
                description='Master techniques for resolving team conflicts',
                content='''<h2>Managing Team Conflict</h2>
<p>Learn effective strategies for addressing and resolving conflicts within your team.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/v4sby5j4NUI"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Conflict Resolution Strategies:</h3>

<h4>1. Competing</h4>
<p>Standing firm on your position - use when quick decisions are needed.</p>

<h4>2. Collaborating</h4>
<p>Working together for win-win solutions - best for important issues.</p>

<h4>3. Compromising</h4>
<p>Finding middle ground - good for time-constrained situations.</p>

<h4>4. Avoiding</h4>
<p>Withdrawing from conflict - appropriate for trivial issues.</p>

<h4>5. Accommodating</h4>
<p>Yielding to others - useful for maintaining harmony.</p>

<h3>Steps to Resolve Conflict:</h3>
<ol>
<li>Acknowledge the conflict exists</li>
<li>Gather information from all sides</li>
<li>Identify the real issue</li>
<li>Generate potential solutions</li>
<li>Evaluate and select best option</li>
<li>Implement and follow up</li>
</ol>''',
                video_url='https://www.youtube.com/watch?v=v4sby5j4NUI',
                order=2,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module1_3,
                title='Motivating Your Team for Success',
                content_type='text',
                duration_minutes=30,
                description='Learn practical techniques to inspire and motivate team members',
                content='''<h2>Motivation Strategies</h2>
<p>Understanding what drives your team members is essential for effective leadership.</p>

<h3>Key Motivational Theories:</h3>

<h4>Maslow's Hierarchy of Needs</h4>
<ol>
<li>Physiological: Basic salary, breaks</li>
<li>Safety: Job security, safe environment</li>
<li>Social: Belonging, team relationships</li>
<li>Esteem: Recognition, achievement</li>
<li>Self-Actualization: Growth, potential</li>
</ol>

<h4>Herzberg's Two-Factor Theory</h4>
<p><strong>Hygiene Factors</strong> (prevent dissatisfaction):</p>
<ul>
<li>Competitive salary and benefits</li>
<li>Good working conditions</li>
<li>Fair company policies</li>
</ul>

<p><strong>Motivators</strong> (create satisfaction):</p>
<ul>
<li>Meaningful work and achievement</li>
<li>Recognition and appreciation</li>
<li>Growth opportunities</li>
<li>Increased responsibility</li>
</ul>

<h3>Practical Motivation Techniques:</h3>
<ul>
<li>Set clear, achievable goals (SMART)</li>
<li>Provide regular, specific feedback</li>
<li>Celebrate wins publicly</li>
<li>Offer development opportunities</li>
<li>Enable autonomy and decision-making</li>
<li>Foster positive team culture</li>
</ul>''',
                order=3,
                is_mandatory=False
            )

            self.stdout.write(self.style.SUCCESS(f'[OK] Course 1 created with {course1.modules.count()} modules'))

            # Add course materials to lessons
            self.stdout.write('Adding training materials to lessons...')
            materials_added = 0

            # Get the path to sample materials
            import os
            from django.conf import settings
            samples_path = os.path.join(settings.MEDIA_ROOT, 'course_materials', 'samples')

            # Add Leadership Assessment PDF to lesson 1-3
            leadership_pdf = os.path.join(samples_path, 'Leadership_Assessment.pdf')
            if os.path.exists(leadership_pdf):
                with open(leadership_pdf, 'rb') as f:
                    material = CourseMaterial.objects.create(
                        lesson=lesson1_3,
                        title='Leadership Style Self-Assessment Worksheet',
                    )
                    material.file.save('Leadership_Assessment.pdf', File(f), save=True)
                    materials_added += 1
                    self.stdout.write(f'  [OK] Added Leadership Assessment PDF')

            # Add Communication Guide PDF to lesson 1-6
            comm_pdf = os.path.join(samples_path, 'Communication_Guide.pdf')
            if os.path.exists(comm_pdf):
                with open(comm_pdf, 'rb') as f:
                    material = CourseMaterial.objects.create(
                        lesson=lesson1_6,
                        title='Non-Verbal Communication Guide',
                    )
                    material.file.save('Communication_Guide.pdf', File(f), save=True)
                    materials_added += 1
                    self.stdout.write(f'  [OK] Added Communication Guide PDF')

            # Course 2: Python Programming
            self.stdout.write('Creating Course 2: Introduction to Python Programming...')
            course2, created = Course.objects.update_or_create(
                code='TECH-101',
                defaults={
                    'title': 'Introduction to Python Programming',
                    'description': '''Learn Python programming from scratch. This beginner-friendly course covers all the fundamentals you need to start coding in Python.

What you'll learn:
• Python syntax and basic programming concepts
• Data types, variables, and operators
• Control flow and loops
• Functions and modules
• Object-oriented programming basics
• Working with files and data

No prior programming experience required!''',
                    'category': 'technical',
                    'level': 'beginner',
                    'instructor': instructor,
                    'duration_hours': 20,
                    'max_students': 50,
                    'passing_score': 70,
                    'status': 'published',
                    'is_mandatory': False
                }
            )
            course2.modules.all().delete()

            module2_1 = CourseModule.objects.create(
                course=course2,
                title='Getting Started with Python',
                description='Set up your development environment and write your first Python program.',
                order=1
            )

            Lesson.objects.create(
                module=module2_1,
                title='Installing Python',
                content_type='text',
                duration_minutes=20,
                description='Download and install Python on your computer',
                content='''<h2>Setting Up Python</h2>
<p>Before we start coding, we need to install Python on your computer.</p>

<h3>Installation Steps:</h3>
<ol>
<li>Visit <a href="https://python.org" target="_blank">python.org</a></li>
<li>Download the latest version for your operating system</li>
<li>Run the installer (remember to check "Add Python to PATH")</li>
<li>Verify installation by opening terminal and typing: <code>python --version</code></li>
</ol>

<h3>Choosing an IDE</h3>
<p>Popular choices for beginners:</p>
<ul>
<li><strong>VS Code:</strong> Lightweight and powerful</li>
<li><strong>PyCharm:</strong> Feature-rich Python IDE</li>
<li><strong>IDLE:</strong> Comes with Python installation</li>
</ul>''',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module2_1,
                title='Your First Python Program',
                content_type='text',
                duration_minutes=25,
                description='Write and run your first Python code',
                content='''<h2>Hello, World!</h2>
<p>Let's write your first Python program - the traditional "Hello, World!"</p>

<h3>The Code</h3>
<pre><code>print("Hello, World!")</code></pre>

<p>This simple program outputs text to the screen. The <code>print()</code> function is one of the most commonly used functions in Python.</p>

<h3>Try It Yourself</h3>
<p>Modify the program to print your name:</p>
<pre><code>print("Hello, my name is [Your Name]")</code></pre>

<h3>Understanding the Code</h3>
<ul>
<li><code>print()</code> is a built-in function</li>
<li>Text inside quotes is called a "string"</li>
<li>Strings can use single ('') or double ("") quotes</li>
</ul>''',
                order=2,
                is_mandatory=True
            )

            lesson2_3 = Lesson.objects.create(
                module=module2_1,
                title='Variables and Data Types',
                content_type='video',
                duration_minutes=35,
                description='Learn about variables and different data types in Python',
                content='''<h2>Variables and Data Types</h2>
<p>Watch this video tutorial on Python variables and data types.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/Z1Yd7upQsXY"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Creating Variables</h3>
<pre><code>name = "Alice"
age = 25
height = 5.7
is_student = True</code></pre>

<h3>Common Data Types</h3>
<ul>
<li><strong>str:</strong> Text (string) - <code>"Hello"</code></li>
<li><strong>int:</strong> Integer numbers - <code>42</code></li>
<li><strong>float:</strong> Decimal numbers - <code>3.14</code></li>
<li><strong>bool:</strong> True or False - <code>True</code></li>
<li><strong>list:</strong> Ordered collection - <code>[1, 2, 3]</code></li>
<li><strong>dict:</strong> Key-value pairs - <code>{"name": "Alice"}</code></li>
</ul>

<h3>Naming Rules</h3>
<ul>
<li>Must start with a letter or underscore</li>
<li>Can contain letters, numbers, and underscores</li>
<li>Case-sensitive (<code>age</code> and <code>Age</code> are different)</li>
<li>Use descriptive names</li>
</ul>

<div style="background: #dcfce7; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;">
    <p><strong>💡 Practice Exercise:</strong></p>
    <p>Download the practice worksheet from Training Materials to test your understanding!</p>
</div>''',
                video_url='https://www.youtube.com/watch?v=Z1Yd7upQsXY',
                order=3,
                is_mandatory=True
            )

            # Module 2-2: Python Control Flow
            module2_2 = CourseModule.objects.create(
                course=course2,
                title='Control Flow and Functions',
                description='Learn about if statements, loops, and functions in Python.',
                order=2
            )

            Lesson.objects.create(
                module=module2_2,
                title='If Statements and Conditionals',
                content_type='video',
                duration_minutes=30,
                description='Learn how to make decisions in your Python code',
                content='''<h2>Control Flow with If Statements</h2>
<p>Watch this tutorial on using conditional statements in Python.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/DZwmZ8Usvnk"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Basic If Statement</h3>
<pre><code>age = 18
if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")</code></pre>

<h3>If-Elif-Else</h3>
<pre><code>score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Your grade is: {grade}")</code></pre>

<h3>Comparison Operators</h3>
<ul>
<li><code>==</code> Equal to</li>
<li><code>!=</code> Not equal to</li>
<li><code>&gt;</code> Greater than</li>
<li><code>&lt;</code> Less than</li>
<li><code>&gt;=</code> Greater than or equal to</li>
<li><code>&lt;=</code> Less than or equal to</li>
</ul>''',
                video_url='https://www.youtube.com/watch?v=DZwmZ8Usvnk',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module2_2,
                title='Loops: For and While',
                content_type='video',
                duration_minutes=35,
                description='Master loops to repeat actions in your code',
                content='''<h2>Loops in Python</h2>
<p>Learn how to use for and while loops to repeat code efficiently.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/6iF8Xb7Z3wQ"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>For Loop</h3>
<pre><code># Loop through a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Loop with range
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4</code></pre>

<h3>While Loop</h3>
<pre><code>count = 0
while count < 5:
    print(count)
    count += 1</code></pre>

<h3>Loop Control</h3>
<ul>
<li><code>break</code> - Exit the loop</li>
<li><code>continue</code> - Skip to next iteration</li>
<li><code>else</code> - Execute after loop completes</li>
</ul>

<div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
    <p><strong>[WARNING] Warning:</strong> Be careful with while loops - make sure they have an exit condition to avoid infinite loops!</p>
</div>''',
                video_url='https://www.youtube.com/watch?v=6iF8Xb7Z3wQ',
                order=2,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module2_2,
                title='Python Functions',
                content_type='video',
                duration_minutes=40,
                description='Create reusable code with functions',
                content='''<h2>Functions in Python</h2>
<p>Functions help you organize and reuse your code effectively.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/9Os0o3wzS_I"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Defining Functions</h3>
<pre><code>def greet(name):
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # Output: Hello, Alice!</code></pre>

<h3>Function with Multiple Parameters</h3>
<pre><code>def calculate_area(length, width):
    area = length * width
    return area

result = calculate_area(5, 3)
print(f"Area: {result}")  # Output: Area: 15</code></pre>

<h3>Default Parameters</h3>
<pre><code>def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))              # Hello, Bob!
print(greet("Bob", "Hi"))        # Hi, Bob!</code></pre>

<h3>Function Benefits</h3>
<ul>
<li>Code reusability</li>
<li>Better organization</li>
<li>Easier testing and debugging</li>
<li>Improved readability</li>
</ul>''',
                video_url='https://www.youtube.com/watch?v=9Os0o3wzS_I',
                order=3,
                is_mandatory=True
            )

            self.stdout.write(self.style.SUCCESS(f'[OK] Course 2 created with {course2.modules.count()} modules'))

            # Add Python Exercises PDF to lesson 2-3
            python_pdf = os.path.join(samples_path, 'Python_Exercises.pdf')
            if os.path.exists(python_pdf):
                with open(python_pdf, 'rb') as f:
                    material = CourseMaterial.objects.create(
                        lesson=lesson2_3,
                        title='Python Practice Exercises Worksheet',
                    )
                    material.file.save('Python_Exercises.pdf', File(f), save=True)
                    materials_added += 1
                    self.stdout.write(f'  [OK] Added Python Exercises PDF')

            # Course 3: Time Management
            self.stdout.write('Creating Course 3: Time Management and Productivity...')
            course3, created = Course.objects.update_or_create(
                code='SOFT-101',
                defaults={
                    'title': 'Time Management and Productivity',
                    'description': '''Master time management techniques to boost your productivity and achieve better work-life balance.

Learn how to:
• Prioritize tasks effectively
• Overcome procrastination
• Use time management tools and techniques
• Manage interruptions and distractions
• Set and achieve goals
• Maintain work-life balance

Increase your efficiency and reduce stress!''',
                    'category': 'soft_skills',
                    'level': 'beginner',
                    'instructor': instructor,
                    'duration_hours': 8,
                    'max_students': 40,
                    'passing_score': 70,
                    'status': 'published',
                    'is_mandatory': False
                }
            )
            course3.modules.all().delete()

            module3_1 = CourseModule.objects.create(
                course=course3,
                title='Fundamentals of Time Management',
                description='Learn the core principles of effective time management.',
                order=1
            )

            Lesson.objects.create(
                module=module3_1,
                title='Understanding Time Management',
                content_type='text',
                duration_minutes=30,
                description='What is time management and why it matters',
                content='''<h2>Time Management Basics</h2>
<p>Time management is the process of planning and controlling how you spend your time on specific activities.</p>

<h3>Why Time Management Matters</h3>
<ul>
<li><strong>Increased Productivity:</strong> Accomplish more in less time</li>
<li><strong>Reduced Stress:</strong> Feel more in control of your workload</li>
<li><strong>Better Work Quality:</strong> More time to focus on important tasks</li>
<li><strong>Improved Work-Life Balance:</strong> More time for personal activities</li>
<li><strong>Career Advancement:</strong> Meet deadlines and exceed expectations</li>
</ul>

<h3>Common Time Wasters</h3>
<ul>
<li>Unnecessary meetings</li>
<li>Social media and internet browsing</li>
<li>Poor planning and disorganization</li>
<li>Saying yes to too many requests</li>
<li>Multitasking (it's less efficient than you think!)</li>
</ul>''',
                order=1,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module3_1,
                title='Prioritization Techniques',
                content_type='video',
                duration_minutes=35,
                description='Learn how to prioritize your tasks effectively',
                content='''<h2>Setting Priorities</h2>
<p>Watch this video to learn proven prioritization techniques.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/tT89OZ7TNwc"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>The Eisenhower Matrix</h3>
<p>Categorize tasks into four quadrants:</p>

<table border="1" cellpadding="10" style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr>
<th style="background: #fee2e2; padding: 15px;">Urgent & Important</th>
<th style="background: #dbeafe; padding: 15px;">Important, Not Urgent</th>
</tr>
<tr>
<td style="padding: 15px;"><strong>Do First</strong><br>Crisis, deadlines, problems</td>
<td style="padding: 15px;"><strong>Schedule</strong><br>Planning, development, prevention</td>
</tr>
<tr>
<th style="background: #fef3c7; padding: 15px;">Urgent, Not Important</th>
<th style="background: #f3f4f6; padding: 15px;">Neither Urgent Nor Important</th>
</tr>
<tr>
<td style="padding: 15px;"><strong>Delegate</strong><br>Interruptions, some emails</td>
<td style="padding: 15px;"><strong>Eliminate</strong><br>Time wasters, busy work</td>
</tr>
</table>

<h3>The ABCDE Method</h3>
<ul>
<li><strong>A:</strong> Very important - must do</li>
<li><strong>B:</strong> Important - should do</li>
<li><strong>C:</strong> Nice to do - minimal consequences</li>
<li><strong>D:</strong> Delegate to someone else</li>
<li><strong>E:</strong> Eliminate - not worth doing</li>
</ul>

<h3>The 80/20 Rule (Pareto Principle)</h3>
<p>80% of results come from 20% of efforts. Identify and focus on the high-impact tasks.</p>''',
                video_url='https://www.youtube.com/watch?v=tT89OZ7TNwc',
                order=2,
                is_mandatory=True
            )

            Lesson.objects.create(
                module=module3_1,
                title='Overcoming Procrastination',
                content_type='video',
                duration_minutes=28,
                description='Strategies to beat procrastination and get things done',
                content='''<h2>Stop Procrastinating, Start Doing</h2>
<p>Learn practical techniques to overcome procrastination.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
    <iframe src="https://www.youtube.com/embed/arj7oStGLkU"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>

<h3>Why We Procrastinate</h3>
<ul>
<li>Fear of failure or success</li>
<li>Perfectionism</li>
<li>Task seems overwhelming</li>
<li>Lack of motivation</li>
<li>Poor time estimation</li>
</ul>

<h3>Anti-Procrastination Strategies</h3>

<h4>1. The Two-Minute Rule</h4>
<p>If it takes less than 2 minutes, do it now.</p>

<h4>2. Break It Down</h4>
<p>Divide large tasks into smaller, manageable steps.</p>

<h4>3. The Pomodoro Technique</h4>
<p>Work for 25 minutes, then take a 5-minute break.</p>

<h4>4. Remove Distractions</h4>
<p>Turn off notifications, close unnecessary tabs.</p>

<h4>5. Just Start</h4>
<p>Commit to working for just 5 minutes - often you'll keep going.</p>

<h4>6. Reward Yourself</h4>
<p>Celebrate completing tasks, no matter how small.</p>

<div style="background: #dcfce7; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;">
    <p><strong>💪 Action Step:</strong> Pick ONE technique to try this week and track your results!</p>
</div>''',
                video_url='https://www.youtube.com/watch?v=arj7oStGLkU',
                order=3,
                is_mandatory=True
            )

            self.stdout.write(self.style.SUCCESS(f'[OK] Course 3 created with {course3.modules.count()} modules'))

            self.stdout.write(self.style.SUCCESS(f'[OK] Added {materials_added} training materials with PDF documents'))

            # Create enrollments
            self.stdout.write('')
            self.stdout.write('Creating sample enrollments...')

            try:
                active_employees = Employee.objects.filter(employment_status='active')[:6]
                enrollments_created = 0

                if not active_employees:
                    self.stdout.write(self.style.WARNING('[WARNING] No active employees found'))
                    self.stdout.write(self.style.WARNING('  Skipping enrollment creation'))
                else:
                    for idx, employee in enumerate(active_employees):
                        # Enroll all in course 1
                        enrollment1, created = CourseEnrollment.objects.get_or_create(
                            employee=employee,
                            course=course1,
                            defaults={
                                'enrollment_date': timezone.now().date(),
                                'status': 'enrolled' if idx % 3 == 0 else 'in_progress',
                                'progress_percentage': 0 if idx % 3 == 0 else (idx * 15) % 100
                            }
                        )
                        if created:
                            enrollments_created += 1

                        # Enroll some in course 2
                        if idx % 2 == 0:
                            enrollment2, created2 = CourseEnrollment.objects.get_or_create(
                                employee=employee,
                                course=course2,
                                defaults={
                                    'enrollment_date': timezone.now().date(),
                                    'status': 'in_progress',
                                    'progress_percentage': (idx * 20) % 100
                                }
                            )
                            if created2:
                                enrollments_created += 1

                        # Enroll some in course 3
                        if idx % 3 == 0:
                            enrollment3, created3 = CourseEnrollment.objects.get_or_create(
                                employee=employee,
                                course=course3,
                                defaults={
                                    'enrollment_date': timezone.now().date(),
                                    'status': 'completed' if idx == 0 else 'enrolled',
                                    'progress_percentage': 100 if idx == 0 else 0,
                                    'final_score': 85 if idx == 0 else None,
                                    'completion_date': timezone.now().date() if idx == 0 else None
                                }
                            )
                            if created3:
                                enrollments_created += 1

                    self.stdout.write(self.style.SUCCESS(f'[OK] Created {enrollments_created} enrollments for {len(active_employees)} employees'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'[WARNING] Could not create enrollments: {str(e)}'))
                self.stdout.write(self.style.WARNING('  Enrollments skipped'))
                enrollments_created = 0

            # Count lesson types and materials
            video_lessons = Lesson.objects.filter(content_type='video').count()
            text_lessons = Lesson.objects.filter(content_type='text').count()
            document_lessons = Lesson.objects.filter(content_type='document').count()
            total_materials = CourseMaterial.objects.count()

            # Summary
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('MOCK DATA GENERATION COMPLETE!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'Courses Created: 3'))
            self.stdout.write(f'   - {course1.code}: {course1.title}')
            self.stdout.write(f'   - {course2.code}: {course2.title}')
            self.stdout.write(f'   - {course3.code}: {course3.title}')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'Modules Created: {CourseModule.objects.count()}'))
            self.stdout.write(self.style.SUCCESS(f'Lessons Created: {Lesson.objects.count()}'))
            self.stdout.write(f'   - Video lessons: {video_lessons} (with embedded YouTube videos)')
            self.stdout.write(f'   - Text lessons: {text_lessons}')
            self.stdout.write(f'   - Document lessons: {document_lessons} (with embedded PDF viewers)')
            self.stdout.write(self.style.SUCCESS(f'Training Materials: {total_materials}'))
            self.stdout.write(f'   - PDF documents with embedded viewer')
            self.stdout.write(f'   - Click "View" button to see documents in-page')
            self.stdout.write(self.style.SUCCESS(f'Enrollments Created: {enrollments_created}'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('View courses at: http://kk.lyp:8000/training/courses/'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('NEW FEATURES:'))
            self.stdout.write('   - PDF files can be viewed directly in the lesson page')
            self.stdout.write('   - Word documents (.docx) can be viewed using Microsoft Office Online')
            self.stdout.write('   - Click the "View" button next to any PDF or Word file')
            self.stdout.write('   - Full-screen modal viewer with embedded document')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'[ERROR] ERROR: {str(e)}'))
            self.stdout.write(self.style.ERROR('='*70))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
