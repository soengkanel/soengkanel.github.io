from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from training.models import (
    Course, CourseModule, Lesson, Instructor
)
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate Leadership and Communication Course with fake data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate Leadership and Communication course...'))

        # Get or create an instructor
        try:
            # Try to get the first superuser or staff user
            instructor_user = User.objects.filter(is_staff=True).first()
            if not instructor_user:
                instructor_user = User.objects.filter(is_superuser=True).first()

            if not instructor_user:
                self.stdout.write(self.style.ERROR('No staff or superuser found. Please create one first.'))
                return

            # Get or create instructor profile
            instructor, created = Instructor.objects.get_or_create(
                user=instructor_user,
                defaults={
                    'bio': 'Leadership development expert with over 15 years of experience in organizational development and executive coaching.',
                    'expertise': 'Leadership, Communication, Team Building',
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created instructor profile for {instructor_user.get_full_name()}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing instructor: {instructor_user.get_full_name()}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating instructor: {str(e)}'))
            return

        # Create the course
        try:
            course, created = Course.objects.get_or_create(
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

            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Course already exists: {course.title}'))
                # Update course details
                course.title = 'Leadership and Communication Essentials'
                course.description = '''Master the fundamental skills of effective leadership and communication.

This comprehensive course covers everything from self-awareness and emotional intelligence to team management and strategic communication. Learn practical techniques that you can apply immediately in your workplace.

Throughout this course, you'll develop:
• Core leadership competencies and styles
• Effective communication strategies for different audiences
• Conflict resolution and negotiation skills
• Team building and motivation techniques
• Decision-making and problem-solving frameworks

Perfect for aspiring leaders, new managers, and anyone looking to enhance their leadership capabilities.'''
                course.category = 'leadership'
                course.level = 'intermediate'
                course.instructor = instructor
                course.duration_hours = 24
                course.status = 'published'
                course.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Updated course: {course.title}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating course: {str(e)}'))
            return

        # Define course structure
        course_structure = [
            {
                'title': 'Introduction to Leadership',
                'description': 'Understand the fundamentals of leadership and discover your leadership style.',
                'lessons': [
                    {
                        'title': 'What is Leadership?',
                        'content_type': 'text',
                        'duration_minutes': 30,
                        'description': 'Explore the definition and core concepts of leadership',
                        'content': '''<h2>Understanding Leadership</h2>
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
<p>While often used interchangeably, leadership and management are distinct concepts:</p>
<ul>
<li><strong>Leadership</strong> is about inspiring and influencing others toward a vision</li>
<li><strong>Management</strong> is about planning, organizing, and controlling resources</li>
</ul>

<p>The best leaders combine both skill sets to drive organizational success.</p>''',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Leadership Styles and Approaches',
                        'content_type': 'video',
                        'duration_minutes': 45,
                        'description': 'Discover different leadership styles and when to use them',
                        'content': '''<h2>Leadership Styles</h2>
<p>Different situations call for different leadership approaches. Understanding various styles helps you adapt your leadership to meet team and organizational needs.</p>

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
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Self-Assessment: Your Leadership Style',
                        'content_type': 'quiz',
                        'duration_minutes': 20,
                        'description': 'Complete a self-assessment to identify your natural leadership tendencies',
                        'content': '''<h2>Leadership Style Self-Assessment</h2>
<p>This assessment will help you understand your natural leadership tendencies and areas for development.</p>

<p>Answer the questions honestly based on your typical behavior, not how you think you should behave.</p>

<h3>Instructions:</h3>
<ol>
<li>Read each scenario carefully</li>
<li>Choose the response that best describes your typical reaction</li>
<li>There are no right or wrong answers</li>
<li>Complete all questions for accurate results</li>
</ol>''',
                        'is_mandatory': True
                    },
                ]
            },
            {
                'title': 'Communication Fundamentals',
                'description': 'Master the essential skills of effective communication in professional settings.',
                'lessons': [
                    {
                        'title': 'Principles of Effective Communication',
                        'content_type': 'text',
                        'duration_minutes': 35,
                        'description': 'Learn the core principles that make communication effective',
                        'content': '''<h2>The Foundation of Effective Communication</h2>
<p>Communication is the lifeblood of any organization. Effective communication ensures that information flows smoothly, relationships strengthen, and goals are achieved.</p>

<h3>The Communication Process</h3>
<ol>
<li><strong>Sender:</strong> The person initiating the message</li>
<li><strong>Encoding:</strong> Converting thoughts into words/symbols</li>
<li><strong>Channel:</strong> The medium through which the message travels</li>
<li><strong>Receiver:</strong> The person receiving the message</li>
<li><strong>Decoding:</strong> Interpreting the message</li>
<li><strong>Feedback:</strong> Response from the receiver</li>
<li><strong>Context:</strong> The environment and circumstances</li>
</ol>

<h3>Barriers to Effective Communication</h3>
<ul>
<li><strong>Physical barriers:</strong> Noise, distance, technical issues</li>
<li><strong>Psychological barriers:</strong> Stress, emotions, attitudes</li>
<li><strong>Language barriers:</strong> Jargon, technical terms, different languages</li>
<li><strong>Cultural barriers:</strong> Different norms and expectations</li>
<li><strong>Perceptual barriers:</strong> Different interpretations and biases</li>
</ul>

<h3>Overcoming Communication Barriers</h3>
<ul>
<li>Choose the right channel for your message</li>
<li>Be clear and concise</li>
<li>Use appropriate language for your audience</li>
<li>Provide context and background</li>
<li>Encourage and listen to feedback</li>
<li>Be aware of non-verbal cues</li>
</ul>''',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Active Listening Skills',
                        'content_type': 'video',
                        'duration_minutes': 40,
                        'description': 'Develop your ability to truly hear and understand others',
                        'content': '''<h2>The Power of Active Listening</h2>
<p>Active listening is one of the most important skills a leader can develop. It goes beyond simply hearing words to truly understanding the message, emotions, and intentions behind them.</p>

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
<li>Mirror appropriate emotions</li>
</ul>

<h4>3. Providing Feedback</h4>
<ul>
<li>Ask clarifying questions</li>
<li>Paraphrase to confirm understanding</li>
<li>Summarize key points</li>
<li>Avoid interrupting</li>
</ul>

<h4>4. Deferring Judgment</h4>
<ul>
<li>Listen without forming immediate opinions</li>
<li>Allow the speaker to finish</li>
<li>Consider their perspective</li>
<li>Separate facts from assumptions</li>
</ul>

<h4>5. Responding Appropriately</h4>
<ul>
<li>Be candid and honest</li>
<li>Provide thoughtful responses</li>
<li>Show empathy and understanding</li>
<li>Respect the speaker's views</li>
</ul>

<h3>Common Listening Mistakes</h3>
<ul>
<li>Interrupting before the speaker finishes</li>
<li>Planning your response while the other person talks</li>
<li>Making assumptions about what they'll say</li>
<li>Getting distracted by side thoughts</li>
<li>Focusing on minor details instead of the main message</li>
</ul>''',
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Non-Verbal Communication',
                        'content_type': 'text',
                        'duration_minutes': 30,
                        'description': 'Understand body language, tone, and other non-verbal cues',
                        'content': '''<h2>The Silent Language of Leadership</h2>
<p>Research shows that 55% of communication is through body language, 38% through tone of voice, and only 7% through words. Understanding non-verbal communication is crucial for effective leadership.</p>

<h3>Types of Non-Verbal Communication</h3>

<h4>1. Facial Expressions</h4>
<p>The face is incredibly expressive and can convey countless emotions without saying a word.</p>
<ul>
<li>Happiness, sadness, anger, surprise, fear, and disgust are universal</li>
<li>Microexpressions reveal true feelings</li>
<li>Smiling can convey warmth and approachability</li>
</ul>

<h4>2. Body Language and Posture</h4>
<ul>
<li><strong>Open posture:</strong> Shows confidence and receptiveness</li>
<li><strong>Closed posture:</strong> May indicate defensiveness or discomfort</li>
<li><strong>Leaning forward:</strong> Shows interest and engagement</li>
<li><strong>Crossed arms:</strong> Can signal resistance or protection</li>
</ul>

<h4>3. Gestures</h4>
<ul>
<li>Hand movements can emphasize points</li>
<li>Cultural differences in gesture meanings</li>
<li>Excessive gesturing can be distracting</li>
</ul>

<h4>4. Eye Contact</h4>
<ul>
<li>Shows attention and interest</li>
<li>Builds trust and connection</li>
<li>Too much can be intimidating</li>
<li>Too little may seem disinterested or dishonest</li>
</ul>

<h4>5. Touch</h4>
<ul>
<li>Handshakes convey confidence</li>
<li>Be mindful of cultural and personal boundaries</li>
<li>Appropriate touch can build rapport</li>
</ul>

<h4>6. Space and Proximity</h4>
<ul>
<li><strong>Intimate space:</strong> 0-18 inches (close relationships)</li>
<li><strong>Personal space:</strong> 18 inches - 4 feet (friends, colleagues)</li>
<li><strong>Social space:</strong> 4-12 feet (professional interactions)</li>
<li><strong>Public space:</strong> 12+ feet (public speaking)</li>
</ul>

<h4>7. Voice (Paralanguage)</h4>
<ul>
<li>Tone, pitch, and volume</li>
<li>Speaking pace and rhythm</li>
<li>Inflection and emphasis</li>
<li>Pauses and silence</li>
</ul>

<h3>Reading Non-Verbal Cues</h3>
<p>When interpreting non-verbal communication:</p>
<ul>
<li>Look for clusters of behaviors, not isolated gestures</li>
<li>Consider context and situation</li>
<li>Be aware of cultural differences</li>
<li>Watch for incongruence between words and body language</li>
<li>Trust your instincts but verify with clarifying questions</li>
</ul>''',
                        'is_mandatory': True
                    },
                ]
            },
            {
                'title': 'Team Building and Collaboration',
                'description': 'Learn how to build high-performing teams and foster collaboration.',
                'lessons': [
                    {
                        'title': 'Building High-Performance Teams',
                        'content_type': 'text',
                        'duration_minutes': 45,
                        'description': 'Understand what makes teams successful',
                        'content': '''<h2>Creating Teams That Excel</h2>
<p>High-performance teams don't happen by accident. They are carefully built, nurtured, and led to achieve extraordinary results.</p>

<h3>Stages of Team Development (Tuckman Model)</h3>

<h4>1. Forming</h4>
<ul>
<li>Team members are polite and cautious</li>
<li>Unclear about roles and responsibilities</li>
<li>Leader provides direction and structure</li>
</ul>

<h4>2. Storming</h4>
<ul>
<li>Conflicts emerge as personalities clash</li>
<li>Competition for influence and position</li>
<li>Leader facilitates resolution and maintains focus</li>
</ul>

<h4>3. Norming</h4>
<ul>
<li>Team establishes working norms</li>
<li>Roles become clearer</li>
<li>Trust and cooperation increase</li>
<li>Leader steps back and empowers team</li>
</ul>

<h4>4. Performing</h4>
<ul>
<li>Team works efficiently toward goals</li>
<li>Strong sense of unity and purpose</li>
<li>High productivity and effectiveness</li>
<li>Leader delegates and monitors</li>
</ul>

<h4>5. Adjourning</h4>
<ul>
<li>Project completion or team disbands</li>
<li>Recognize achievements</li>
<li>Reflect on learnings</li>
</ul>

<h3>Characteristics of High-Performance Teams</h3>
<ul>
<li><strong>Clear Goals:</strong> Shared understanding of objectives</li>
<li><strong>Defined Roles:</strong> Everyone knows their responsibilities</li>
<li><strong>Open Communication:</strong> Honest and frequent dialogue</li>
<li><strong>Mutual Trust:</strong> Team members rely on each other</li>
<li><strong>Constructive Conflict:</strong> Disagreements lead to better solutions</li>
<li><strong>Strong Commitment:</strong> Dedication to team success</li>
<li><strong>Results Focus:</strong> Emphasis on achieving outcomes</li>
</ul>''',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Conflict Resolution Strategies',
                        'content_type': 'video',
                        'duration_minutes': 50,
                        'description': 'Master techniques for resolving team conflicts constructively',
                        'content': '''<h2>Turning Conflict into Opportunity</h2>
<p>Conflict is inevitable in any team. The key is not avoiding it, but managing it effectively to strengthen the team and improve outcomes.</p>

<h3>The Five Conflict Resolution Styles (Thomas-Kilmann)</h3>

<h4>1. Competing (Assertive, Uncooperative)</h4>
<ul>
<li>Standing firm on your position</li>
<li>Best when: Quick decisions needed, unpopular actions required</li>
<li>Drawback: Can damage relationships</li>
</ul>

<h4>2. Collaborating (Assertive, Cooperative)</h4>
<ul>
<li>Working together to find win-win solutions</li>
<li>Best when: Both concerns are important, commitment needed</li>
<li>Drawback: Time-consuming</li>
</ul>

<h4>3. Compromising (Moderate on both)</h4>
<ul>
<li>Finding middle ground</li>
<li>Best when: Goals moderately important, time pressured</li>
<li>Drawback: No one fully satisfied</li>
</ul>

<h4>4. Avoiding (Unassertive, Uncooperative)</h4>
<ul>
<li>Withdrawing from the conflict</li>
<li>Best when: Issue is trivial, need time to cool down</li>
<li>Drawback: Problems remain unresolved</li>
</ul>

<h4>5. Accommodating (Unassertive, Cooperative)</h4>
<ul>
<li>Yielding to others' concerns</li>
<li>Best when: Maintaining harmony is crucial, you're wrong</li>
<li>Drawback: Your concerns ignored</li>
</ul>

<h3>Steps to Resolve Conflict</h3>
<ol>
<li><strong>Acknowledge the conflict:</strong> Don't ignore or minimize</li>
<li><strong>Gather information:</strong> Understand all perspectives</li>
<li><strong>Identify the real issue:</strong> Look beyond symptoms</li>
<li><strong>Generate options:</strong> Brainstorm possible solutions</li>
<li><strong>Evaluate solutions:</strong> Consider pros and cons</li>
<li><strong>Agree on action:</strong> Commit to a course of action</li>
<li><strong>Follow up:</strong> Ensure the solution is working</li>
</ol>''',
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Motivating Your Team',
                        'content_type': 'text',
                        'duration_minutes': 35,
                        'description': 'Learn how to inspire and motivate team members',
                        'content': '''<h2>Inspiring Peak Performance</h2>
<p>Motivation is the fuel that drives performance. Understanding what motivates your team members is essential for effective leadership.</p>

<h3>Theories of Motivation</h3>

<h4>Maslow's Hierarchy of Needs</h4>
<ol>
<li><strong>Physiological:</strong> Basic needs (salary, breaks)</li>
<li><strong>Safety:</strong> Job security, safe environment</li>
<li><strong>Social:</strong> Belonging, relationships</li>
<li><strong>Esteem:</strong> Recognition, status</li>
<li><strong>Self-Actualization:</strong> Growth, reaching potential</li>
</ol>

<h4>Herzberg's Two-Factor Theory</h4>
<p><strong>Hygiene Factors</strong> (prevent dissatisfaction):</p>
<ul>
<li>Salary and benefits</li>
<li>Working conditions</li>
<li>Company policies</li>
<li>Job security</li>
</ul>

<p><strong>Motivators</strong> (create satisfaction):</p>
<ul>
<li>Achievement</li>
<li>Recognition</li>
<li>Responsibility</li>
<li>Growth opportunities</li>
</ul>

<h3>Practical Motivation Strategies</h3>

<h4>1. Provide Clear Goals and Expectations</h4>
<ul>
<li>Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)</li>
<li>Ensure understanding of how individual work contributes to team/company success</li>
</ul>

<h4>2. Offer Recognition and Rewards</h4>
<ul>
<li>Celebrate achievements publicly</li>
<li>Provide specific, timely feedback</li>
<li>Offer both formal and informal recognition</li>
</ul>

<h4>3. Enable Growth and Development</h4>
<ul>
<li>Provide training opportunities</li>
<li>Assign challenging projects</li>
<li>Support career advancement</li>
</ul>

<h4>4. Foster Autonomy</h4>
<ul>
<li>Delegate meaningful tasks</li>
<li>Allow flexibility in how work is done</li>
<li>Trust team members to make decisions</li>
</ul>

<h4>5. Create a Positive Environment</h4>
<ul>
<li>Build strong relationships</li>
<li>Encourage open communication</li>
<li>Address conflicts promptly</li>
<li>Maintain work-life balance</li>
</ul>''',
                        'is_mandatory': False
                    },
                ]
            },
            {
                'title': 'Decision Making and Problem Solving',
                'description': 'Develop frameworks for making effective decisions and solving complex problems.',
                'lessons': [
                    {
                        'title': 'Strategic Decision-Making',
                        'content_type': 'text',
                        'duration_minutes': 40,
                        'description': 'Learn systematic approaches to making important decisions',
                        'content': '''<h2>Making Decisions That Matter</h2>
<p>Leaders are constantly making decisions. The quality of these decisions directly impacts team performance and organizational success.</p>

<h3>Types of Decisions</h3>

<h4>Programmed Decisions</h4>
<ul>
<li>Routine and repetitive</li>
<li>Clear rules and procedures</li>
<li>Examples: Approving time off, ordering supplies</li>
</ul>

<h4>Non-Programmed Decisions</h4>
<ul>
<li>Unique and complex</li>
<li>Require judgment and creativity</li>
<li>Examples: Strategic planning, crisis response</li>
</ul>

<h3>Decision-Making Models</h3>

<h4>Rational Decision-Making Process</h4>
<ol>
<li><strong>Identify the problem:</strong> Clearly define what needs to be decided</li>
<li><strong>Gather information:</strong> Collect relevant data and facts</li>
<li><strong>Identify alternatives:</strong> Generate multiple possible solutions</li>
<li><strong>Evaluate alternatives:</strong> Assess pros and cons of each option</li>
<li><strong>Choose the best alternative:</strong> Select the optimal solution</li>
<li><strong>Implement the decision:</strong> Put the solution into action</li>
<li><strong>Evaluate the results:</strong> Monitor outcomes and adjust as needed</li>
</ol>

<h4>SWOT Analysis</h4>
<ul>
<li><strong>Strengths:</strong> Internal positive factors</li>
<li><strong>Weaknesses:</strong> Internal limitations</li>
<li><strong>Opportunities:</strong> External favorable conditions</li>
<li><strong>Threats:</strong> External challenges</li>
</ul>

<h3>Common Decision-Making Pitfalls</h3>
<ul>
<li><strong>Confirmation bias:</strong> Seeking information that confirms existing beliefs</li>
<li><strong>Anchoring:</strong> Over-relying on the first piece of information</li>
<li><strong>Groupthink:</strong> Going along with the group to avoid conflict</li>
<li><strong>Analysis paralysis:</strong> Over-analyzing and delaying decisions</li>
<li><strong>Sunk cost fallacy:</strong> Continuing because of past investment</li>
</ul>

<h3>Tips for Better Decisions</h3>
<ul>
<li>Involve the right people</li>
<li>Consider multiple perspectives</li>
<li>Use data to inform, not dictate</li>
<li>Set a decision deadline</li>
<li>Trust your intuition (with experience)</li>
<li>Learn from past decisions</li>
</ul>''',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Creative Problem Solving',
                        'content_type': 'video',
                        'duration_minutes': 45,
                        'description': 'Apply innovative techniques to solve complex challenges',
                        'content': '''<h2>Thinking Outside the Box</h2>
<p>Complex problems require creative solutions. Leaders must foster environments where innovative thinking thrives.</p>

<h3>Problem-Solving Techniques</h3>

<h4>1. Brainstorming</h4>
<p>Generate many ideas quickly without judgment</p>
<ul>
<li>Set a time limit (10-15 minutes)</li>
<li>Encourage wild ideas</li>
<li>Build on others' suggestions</li>
<li>Defer criticism and evaluation</li>
<li>Go for quantity over quality initially</li>
</ul>

<h4>2. The 5 Whys</h4>
<p>Dig deeper to find root causes</p>
<ul>
<li>State the problem</li>
<li>Ask "Why did this happen?"</li>
<li>Continue asking "Why?" for each answer</li>
<li>Typically reveals root cause by the fifth why</li>
</ul>

<h4>3. Mind Mapping</h4>
<p>Visual tool for organizing thoughts</p>
<ul>
<li>Put main problem in center</li>
<li>Branch out with related ideas</li>
<li>Create sub-branches for details</li>
<li>Use colors and images</li>
</ul>

<h4>4. Six Thinking Hats (Edward de Bono)</h4>
<ul>
<li><strong>White Hat:</strong> Facts and information</li>
<li><strong>Red Hat:</strong> Emotions and intuition</li>
<li><strong>Black Hat:</strong> Critical judgment</li>
<li><strong>Yellow Hat:</strong> Positive outlook</li>
<li><strong>Green Hat:</strong> Creativity and new ideas</li>
<li><strong>Blue Hat:</strong> Process control</li>
</ul>

<h4>5. SCAMPER Technique</h4>
<p>Questions to spark creative thinking:</p>
<ul>
<li><strong>S</strong>ubstitute: What can be replaced?</li>
<li><strong>C</strong>ombine: What can be merged together?</li>
<li><strong>A</strong>dapt: What can be adjusted?</li>
<li><strong>M</strong>odify: What can be changed?</li>
<li><strong>P</strong>ut to other uses: How else can it be used?</li>
<li><strong>E</strong>liminate: What can be removed?</li>
<li><strong>R</strong>everse: What can be done differently?</li>
</ul>

<h3>Fostering Creative Thinking</h3>
<ul>
<li>Create psychological safety</li>
<li>Encourage diverse perspectives</li>
<li>Allow time for reflection</li>
<li>Reward creative attempts, even failures</li>
<li>Provide resources and support</li>
<li>Challenge assumptions</li>
</ul>''',
                        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        'is_mandatory': True
                    },
                ]
            },
            {
                'title': 'Leading Through Change',
                'description': 'Navigate organizational change and lead your team through transitions.',
                'lessons': [
                    {
                        'title': 'Change Management Fundamentals',
                        'content_type': 'text',
                        'duration_minutes': 40,
                        'description': 'Understand the dynamics of organizational change',
                        'content': '''<h2>Leading in Times of Change</h2>
<p>Change is the only constant in modern organizations. Effective leaders don't just manage change—they champion it.</p>

<h3>Why Change Initiatives Fail</h3>
<ul>
<li>Lack of clear vision and communication</li>
<li>Insufficient leadership support</li>
<li>Employee resistance not addressed</li>
<li>Inadequate resources and training</li>
<li>Trying to change too much too fast</li>
<li>Declaring victory too soon</li>
</ul>

<h3>Kotter's 8-Step Change Model</h3>

<ol>
<li><strong>Create Urgency:</strong> Help others see the need for change</li>
<li><strong>Build a Guiding Coalition:</strong> Assemble a group with power to lead</li>
<li><strong>Form a Strategic Vision:</strong> Create clear vision and strategy</li>
<li><strong>Enlist a Volunteer Army:</strong> Communicate to gain buy-in</li>
<li><strong>Enable Action:</strong> Remove obstacles and barriers</li>
<li><strong>Generate Short-Term Wins:</strong> Create and celebrate quick wins</li>
<li><strong>Sustain Acceleration:</strong> Build on momentum</li>
<li><strong>Institute Change:</strong> Anchor changes in culture</li>
</ol>

<h3>Managing Resistance to Change</h3>

<h4>Common Reasons for Resistance:</h4>
<ul>
<li>Fear of the unknown</li>
<li>Loss of control or status</li>
<li>Concern about competence</li>
<li>Previous negative experiences</li>
<li>Lack of trust in leadership</li>
<li>Different assessments of the situation</li>
</ul>

<h4>Strategies to Overcome Resistance:</h4>
<ul>
<li><strong>Communication:</strong> Explain why, what, and how</li>
<li><strong>Participation:</strong> Involve people in planning</li>
<li><strong>Support:</strong> Provide training and resources</li>
<li><strong>Negotiation:</strong> Address legitimate concerns</li>
<li><strong>Timing:</strong> Implement at the right pace</li>
</ul>

<h3>The Role of Leaders in Change</h3>
<ul>
<li>Model the change you want to see</li>
<li>Communicate constantly and consistently</li>
<li>Listen to concerns and feedback</li>
<li>Celebrate progress and milestones</li>
<li>Stay committed through difficulties</li>
<li>Be transparent about challenges</li>
</ul>''',
                        'is_mandatory': True
                    },
                    {
                        'title': 'Building Organizational Resilience',
                        'content_type': 'text',
                        'duration_minutes': 35,
                        'description': 'Create teams that thrive in uncertainty',
                        'content': '''<h2>Thriving in Uncertainty</h2>
<p>Resilient organizations don't just survive change—they grow stronger through it. Leaders play a crucial role in building this resilience.</p>

<h3>Characteristics of Resilient Organizations</h3>

<h4>1. Adaptive Capacity</h4>
<ul>
<li>Flexible structures and processes</li>
<li>Quick to learn and adjust</li>
<li>Embrace experimentation</li>
<li>Learn from failures</li>
</ul>

<h4>2. Strong Networks</h4>
<ul>
<li>Deep internal relationships</li>
<li>External partnerships and connections</li>
<li>Open communication channels</li>
<li>Knowledge sharing culture</li>
</ul>

<h4>3. Leadership Depth</h4>
<ul>
<li>Leaders at all levels</li>
<li>Succession planning</li>
<li>Distributed decision-making</li>
<li>Development focus</li>
</ul>

<h4>4. Cultural Strength</h4>
<ul>
<li>Clear values and purpose</li>
<li>Psychological safety</li>
<li>Innovation mindset</li>
<li>Employee engagement</li>
</ul>

<h3>Building Personal Resilience</h3>

<h4>For Yourself:</h4>
<ul>
<li>Maintain perspective</li>
<li>Practice self-care</li>
<li>Build strong relationships</li>
<li>Stay flexible and adaptable</li>
<li>Focus on what you can control</li>
<li>Maintain optimism</li>
</ul>

<h4>For Your Team:</h4>
<ul>
<li>Foster trust and connection</li>
<li>Provide stability and structure</li>
<li>Encourage open dialogue</li>
<li>Recognize and reward adaptability</li>
<li>Support work-life balance</li>
<li>Celebrate small wins</li>
</ul>

<h3>Strategies for Leading Through Crisis</h3>
<ol>
<li><strong>Stay calm:</strong> Your demeanor sets the tone</li>
<li><strong>Assess quickly:</strong> Gather facts and understand the situation</li>
<li><strong>Communicate clearly:</strong> Provide frequent updates</li>
<li><strong>Prioritize:</strong> Focus on what's most important</li>
<li><strong>Empower:</strong> Give people authority to act</li>
<li><strong>Show empathy:</strong> Acknowledge the human impact</li>
<li><strong>Plan ahead:</strong> Think beyond the immediate crisis</li>
<li><strong>Learn:</strong> Extract lessons for the future</li>
</ol>

<h3>After the Storm</h3>
<p>When the crisis passes:</p>
<ul>
<li>Acknowledge and thank the team</li>
<li>Conduct a thorough debrief</li>
<li>Document lessons learned</li>
<li>Update plans and procedures</li>
<li>Rebuild morale and energy</li>
<li>Look forward with optimism</li>
</ul>''',
                        'is_mandatory': False
                    },
                    {
                        'title': 'Course Wrap-Up and Action Planning',
                        'content_type': 'text',
                        'duration_minutes': 30,
                        'description': 'Reflect on your learning and create your leadership action plan',
                        'content': '''<h2>Your Leadership Journey Continues</h2>
<p>Congratulations on completing the Leadership and Communication Essentials course! Now it's time to put your learning into action.</p>

<h3>Key Takeaways</h3>

<h4>Leadership Foundations</h4>
<ul>
<li>Leadership is about influence, not position</li>
<li>Different situations require different styles</li>
<li>Self-awareness is the foundation of effective leadership</li>
</ul>

<h4>Communication Excellence</h4>
<ul>
<li>Effective communication is bidirectional</li>
<li>Active listening is as important as speaking</li>
<li>Non-verbal communication speaks volumes</li>
</ul>

<h4>Team Leadership</h4>
<ul>
<li>High-performance teams are intentionally built</li>
<li>Conflict can be productive when managed well</li>
<li>Motivation comes from understanding individual needs</li>
</ul>

<h4>Decision Making</h4>
<ul>
<li>Use structured approaches for important decisions</li>
<li>Creative thinking solves complex problems</li>
<li>Learn from both successes and failures</li>
</ul>

<h4>Leading Change</h4>
<ul>
<li>Change is constant—embrace it</li>
<li>Communication and support overcome resistance</li>
<li>Resilience can be developed and strengthened</li>
</ul>

<h3>Creating Your Action Plan</h3>

<h4>Reflect on Your Learning:</h4>
<ol>
<li>What were your most important insights?</li>
<li>What surprised you?</li>
<li>What challenged your thinking?</li>
<li>What confirmed what you already knew?</li>
</ol>

<h4>Set Development Goals:</h4>
<p>Choose 2-3 areas to focus on:</p>
<ul>
<li>What specific skills will you develop?</li>
<li>How will you practice them?</li>
<li>Who can support your development?</li>
<li>How will you measure progress?</li>
</ul>

<h4>Plan Your First Steps:</h4>
<ul>
<li>What will you do differently tomorrow?</li>
<li>What conversation will you have this week?</li>
<li>What new practice will you establish?</li>
<li>Who will you ask for feedback?</li>
</ul>

<h3>Continuing Your Development</h3>

<h4>Resources for Ongoing Learning:</h4>
<ul>
<li>Join leadership development programs</li>
<li>Read leadership books and articles</li>
<li>Find a mentor or coach</li>
<li>Attend workshops and conferences</li>
<li>Join professional networks</li>
<li>Practice, reflect, and refine</li>
</ul>

<h4>Key Leadership Books to Consider:</h4>
<ul>
<li>"Leaders Eat Last" by Simon Sinek</li>
<li>"The Five Dysfunctions of a Team" by Patrick Lencioni</li>
<li>"Dare to Lead" by Brené Brown</li>
<li>"Good to Great" by Jim Collins</li>
<li>"The 7 Habits of Highly Effective People" by Stephen Covey</li>
</ul>

<h3>Final Thoughts</h3>
<blockquote>
<p>"Leadership is not about being in charge. It's about taking care of those in your charge."</p>
<p>— Simon Sinek</p>
</blockquote>

<p>Remember: Leadership is a journey, not a destination. Keep learning, practicing, and growing. Your team, your organization, and your career will benefit from your commitment to leadership excellence.</p>

<p><strong>Thank you for your participation. Now go lead with confidence and compassion!</strong></p>''',
                        'is_mandatory': True
                    },
                ]
            },
        ]

        # Create modules and lessons
        try:
            for module_order, module_data in enumerate(course_structure, 1):
                module, module_created = CourseModule.objects.get_or_create(
                    course=course,
                    title=module_data['title'],
                    defaults={
                        'description': module_data['description'],
                        'order': module_order
                    }
                )

                if module_created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created module: {module.title}'))
                else:
                    # Update existing module
                    module.description = module_data['description']
                    module.order = module_order
                    module.save()
                    # Clear existing lessons to recreate
                    module.lessons.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Updated module: {module.title}'))

                # Create lessons
                for lesson_order, lesson_data in enumerate(module_data['lessons'], 1):
                    lesson, lesson_created = Lesson.objects.get_or_create(
                        module=module,
                        title=lesson_data['title'],
                        defaults={
                            'content_type': lesson_data['content_type'],
                            'duration_minutes': lesson_data['duration_minutes'],
                            'description': lesson_data['description'],
                            'content': lesson_data['content'],
                            'video_url': lesson_data.get('video_url', ''),
                            'order': lesson_order,
                            'is_mandatory': lesson_data.get('is_mandatory', True)
                        }
                    )

                    if lesson_created:
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Created lesson: {lesson.title}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'    • Lesson already exists: {lesson.title}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating modules/lessons: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✓ Successfully populated Leadership and Communication course!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\nCourse Details:')
        self.stdout.write(f'  • Code: {course.code}')
        self.stdout.write(f'  • Title: {course.title}')
        self.stdout.write(f'  • Modules: {course.modules.count()}')
        self.stdout.write(f'  • Total Lessons: {sum(module.lessons.count() for module in course.modules.all())}')
        self.stdout.write(f'  • Status: {course.status}')
        self.stdout.write(f'\nView course at: /training/courses/{course.pk}/')
        self.stdout.write(self.style.SUCCESS('\nYou can now add training materials to lessons through the web interface!'))
