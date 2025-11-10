# Run this with: python manage.py shell < populate_course_data.py

from django.contrib.auth import get_user_model
from training.models import Course, CourseModule, Lesson
from hr.models import Employee

User = get_user_model()

print("Starting data population...")

# Get first staff user
try:
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        print("No staff user found! Creating course without instructor...")
        instructor_id = None
    else:
        # Try to get employee associated with this user
        try:
            employee = Employee.objects.filter(user=staff_user).first()
            instructor_id = employee.id if employee else None
            print(f"Found instructor: {staff_user.get_full_name()}")
        except:
            instructor_id = None
            print("Could not find employee, creating course without instructor")

    # Create or update course
    course, created = Course.objects.update_or_create(
        code='LEAD-101',
        defaults={
            'title': 'Leadership and Communication Essentials',
            'description': '''Master the fundamental skills of effective leadership and communication.

This comprehensive course covers everything from self-awareness and emotional intelligence to team management and strategic communication.

Throughout this course, you'll develop:
• Core leadership competencies and styles
• Effective communication strategies
• Conflict resolution and negotiation skills
• Team building and motivation techniques
• Decision-making frameworks

Perfect for aspiring leaders and new managers.''',
            'category': 'leadership',
            'level': 'intermediate',
            'instructor_id': instructor_id,
            'duration_hours': 24,
            'max_students': 30,
            'passing_score': 75,
            'status': 'published',
            'is_mandatory': False
        }
    )

    if created:
        print(f"✓ Created course: {course.title}")
    else:
        print(f"✓ Updated course: {course.title}")

    # Delete existing modules to recreate
    course.modules.all().delete()

    # Module 1
    module1 = CourseModule.objects.create(
        course=course,
        title='Introduction to Leadership',
        description='Understand the fundamentals of leadership and discover your leadership style.',
        order=1
    )
    print(f"  ✓ Created module: {module1.title}")

    Lesson.objects.create(
        module=module1,
        title='What is Leadership?',
        content_type='text',
        duration_minutes=30,
        description='Explore the definition and core concepts of leadership',
        content='''<h2>Understanding Leadership</h2>
<p>Leadership is the art of motivating a group of people to act toward achieving a common goal.</p>

<h3>Key Characteristics:</h3>
<ul>
<li><strong>Vision:</strong> Seeing the big picture</li>
<li><strong>Communication:</strong> Articulating ideas clearly</li>
<li><strong>Integrity:</strong> Being honest and consistent</li>
<li><strong>Empathy:</strong> Understanding others</li>
</ul>''',
        order=1,
        is_mandatory=True
    )
    print(f"    ✓ Created lesson: What is Leadership?")

    Lesson.objects.create(
        module=module1,
        title='Leadership Styles',
        content_type='video',
        duration_minutes=45,
        description='Discover different leadership styles',
        content='''<h2>Leadership Styles</h2>
<p>Different situations call for different approaches.</p>

<h3>Common Styles:</h3>
<ul>
<li><strong>Transformational:</strong> Inspires and motivates</li>
<li><strong>Servant:</strong> Focuses on serving others</li>
<li><strong>Democratic:</strong> Involves team in decisions</li>
<li><strong>Situational:</strong> Adapts to the situation</li>
</ul>''',
        video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        order=2,
        is_mandatory=True
    )
    print(f"    ✓ Created lesson: Leadership Styles")

    # Module 2
    module2 = CourseModule.objects.create(
        course=course,
        title='Communication Fundamentals',
        description='Master essential communication skills.',
        order=2
    )
    print(f"  ✓ Created module: {module2.title}")

    Lesson.objects.create(
        module=module2,
        title='Effective Communication',
        content_type='text',
        duration_minutes=35,
        description='Learn core communication principles',
        content='''<h2>Communication Principles</h2>
<p>Effective communication ensures smooth information flow.</p>

<h3>Barriers to Communication:</h3>
<ul>
<li>Physical barriers (noise, distance)</li>
<li>Psychological barriers (stress, emotions)</li>
<li>Language barriers (jargon, technical terms)</li>
<li>Cultural barriers (different norms)</li>
</ul>''',
        order=1,
        is_mandatory=True
    )
    print(f"    ✓ Created lesson: Effective Communication")

    Lesson.objects.create(
        module=module2,
        title='Active Listening',
        content_type='video',
        duration_minutes=40,
        description='Develop active listening skills',
        content='''<h2>Active Listening</h2>
<p>Truly hearing and understanding others.</p>

<h3>Components:</h3>
<ul>
<li>Pay attention</li>
<li>Show you're listening</li>
<li>Provide feedback</li>
<li>Defer judgment</li>
<li>Respond appropriately</li>
</ul>''',
        video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        order=2,
        is_mandatory=True
    )
    print(f"    ✓ Created lesson: Active Listening")

    # Module 3
    module3 = CourseModule.objects.create(
        course=course,
        title='Team Building',
        description='Build high-performing teams.',
        order=3
    )
    print(f"  ✓ Created module: {module3.title}")

    Lesson.objects.create(
        module=module3,
        title='High-Performance Teams',
        content_type='text',
        duration_minutes=45,
        description='What makes teams successful',
        content='''<h2>Team Success</h2>
<p>High-performance teams are intentionally built.</p>

<h3>Characteristics:</h3>
<ul>
<li>Clear goals</li>
<li>Defined roles</li>
<li>Open communication</li>
<li>Mutual trust</li>
<li>Results focus</li>
</ul>''',
        order=1,
        is_mandatory=True
    )
    print(f"    ✓ Created lesson: High-Performance Teams")

    print("\n" + "="*70)
    print(f"✓ SUCCESS! Course created with {course.modules.count()} modules")
    print(f"  Total lessons: {sum(m.lessons.count() for m in course.modules.all())}")
    print(f"\nView at: http://kk.lyp:8000/training/courses/{course.pk}/")
    print("="*70)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
