import React from 'react';
import { useNavigate } from 'react-router';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  ShoppingCart,
  Utensils,
  BarChart3,
  Users,
  Package,
  Clock,
  Shield,
  Zap,
  CheckCircle,
  ArrowRight,
  Menu,
  X,
} from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const features = [
    {
      icon: <ShoppingCart className="w-8 h-8 text-blue-600" />,
      title: 'Retail Management',
      description: 'Complete inventory tracking, barcode scanning, and stock alerts for retail businesses.',
    },
    {
      icon: <Utensils className="w-8 h-8 text-orange-600" />,
      title: 'Restaurant & F&B',
      description: 'Table management, kitchen display system, and menu customization for restaurants.',
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-green-600" />,
      title: 'Real-time Analytics',
      description: 'Track sales, inventory, and performance metrics in real-time with detailed reports.',
    },
    {
      icon: <Users className="w-8 h-8 text-purple-600" />,
      title: 'Employee Management',
      description: 'Manage staff roles, shift reports, and cashier performance across branches.',
    },
    {
      icon: <Package className="w-8 h-8 text-red-600" />,
      title: 'Multi-Store Support',
      description: 'Manage multiple branches from a single dashboard with centralized control.',
    },
    {
      icon: <Clock className="w-8 h-8 text-indigo-600" />,
      title: 'Kitchen Display System',
      description: 'Real-time order tracking for kitchen with preparation time estimates.',
    },
  ];

  const businessTypes = [
    {
      title: 'Retail Store',
      description: 'Perfect for clothing, electronics, and general merchandise stores',
      features: ['Barcode Scanning', 'Inventory Management', 'Customer Loyalty'],
      icon: '🛍️',
    },
    {
      title: 'Restaurant',
      description: 'Complete solution for cafes, restaurants, and food establishments',
      features: ['Table Management', 'Kitchen Orders', 'Menu Modifiers'],
      icon: '🍽️',
    },
    {
      title: 'Hybrid Business',
      description: 'Run both retail and F&B operations seamlessly',
      features: ['Unified POS', 'Mixed Inventory', 'Flexible Reports'],
      icon: '🏪',
    },
  ];

  const pricingPlans = [
    {
      name: 'Starter',
      price: '$29',
      period: '/month',
      features: [
        '1 Branch',
        'Up to 500 Products',
        'Basic Reports',
        'Email Support',
        'Mobile App Access',
      ],
      highlight: false,
    },
    {
      name: 'Professional',
      price: '$79',
      period: '/month',
      features: [
        '5 Branches',
        'Unlimited Products',
        'Advanced Analytics',
        'Priority Support',
        'Kitchen Display System',
        'Table Management',
      ],
      highlight: true,
    },
    {
      name: 'Enterprise',
      price: '$199',
      period: '/month',
      features: [
        'Unlimited Branches',
        'Unlimited Products',
        'Custom Reports',
        '24/7 Phone Support',
        'API Access',
        'Custom Integrations',
        'Dedicated Account Manager',
      ],
      highlight: false,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">NGPOS</h1>
              <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                Free 14-day trial
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition">
                Features
              </a>
              <a href="#solutions" className="text-gray-700 hover:text-blue-600 transition">
                Solutions
              </a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition">
                Pricing
              </a>
              <a href="#contact" className="text-gray-700 hover:text-blue-600 transition">
                Contact
              </a>
              <Button
                variant="outline"
                onClick={() => navigate('/auth/login')}
              >
                Sign In
              </Button>
              <Button onClick={() => navigate('/auth/register')}>
                Get Started
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-700 hover:text-blue-600"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-3 space-y-3">
              <a href="#features" className="block text-gray-700 hover:text-blue-600">
                Features
              </a>
              <a href="#solutions" className="block text-gray-700 hover:text-blue-600">
                Solutions
              </a>
              <a href="#pricing" className="block text-gray-700 hover:text-blue-600">
                Pricing
              </a>
              <a href="#contact" className="block text-gray-700 hover:text-blue-600">
                Contact
              </a>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate('/auth/login')}
              >
                Sign In
              </Button>
              <Button className="w-full" onClick={() => navigate('/auth/register')}>
                Get Started
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-white to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Simplify Your Business
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                Operations Today
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Powerful POS system for retail stores and restaurants. Manage sales, inventory,
              tables, and kitchen orders all in one place.
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <Button
                size="lg"
                className="text-lg px-8 py-6"
                onClick={() => navigate('/auth/register')}
              >
                Start Free Trial <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-6"
                onClick={() => (window.location.href = '#contact')}
              >
                Request Demo
              </Button>
            </div>

            {/* Trust Badges */}
            <div className="flex flex-wrap justify-center gap-8 text-gray-600">
              <div className="flex items-center">
                <Shield className="w-5 h-5 mr-2 text-green-600" />
                <span>Secure & Compliant</span>
              </div>
              <div className="flex items-center">
                <Zap className="w-5 h-5 mr-2 text-yellow-600" />
                <span>Lightning Fast</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-blue-600" />
                <span>24/7 Support</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl text-gray-600">
              Comprehensive features designed for modern businesses
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="p-6 hover:shadow-xl transition-shadow duration-300"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Business Solutions Section */}
      <section id="solutions" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for Your Business Type
            </h2>
            <p className="text-xl text-gray-600">
              Tailored solutions for retail, restaurants, or hybrid operations
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {businessTypes.map((business, index) => (
              <Card key={index} className="p-8 text-center hover:shadow-xl transition-all">
                <div className="text-6xl mb-4">{business.icon}</div>
                <h3 className="text-2xl font-bold mb-2">{business.title}</h3>
                <p className="text-gray-600 mb-6">{business.description}</p>
                <div className="space-y-2">
                  {business.features.map((feature, fIndex) => (
                    <div key={fIndex} className="flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your business size
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <Card
                key={index}
                className={`p-8 ${
                  plan.highlight
                    ? 'border-4 border-blue-600 shadow-2xl scale-105'
                    : 'border border-gray-200'
                }`}
              >
                {plan.highlight && (
                  <div className="bg-blue-600 text-white text-sm font-semibold px-3 py-1 rounded-full inline-block mb-4">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  className={`w-full ${
                    plan.highlight ? 'bg-blue-600 hover:bg-blue-700' : ''
                  }`}
                  variant={plan.highlight ? 'default' : 'outline'}
                  onClick={() => navigate('/auth/register')}
                >
                  Get Started
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of businesses using NGPOS to streamline operations
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-6"
              onClick={() => navigate('/auth/register')}
            >
              Start Your Free Trial
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-blue-600 text-lg px-8 py-6"
              onClick={() => (window.location.href = '#contact')}
            >
              Schedule a Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Get in Touch</h2>
            <p className="text-xl text-gray-600">
              Have questions? We're here to help!
            </p>
          </div>

          <Card className="p-8">
            <form className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                    placeholder="john@example.com"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Type
                </label>
                <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent">
                  <option>Retail Store</option>
                  <option>Restaurant</option>
                  <option>Cafe</option>
                  <option>Hybrid Business</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message
                </label>
                <textarea
                  rows="4"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                  placeholder="Tell us about your business needs..."
                ></textarea>
              </div>
              <Button type="submit" size="lg" className="w-full">
                Send Message
              </Button>
            </form>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">NGPOS</h3>
              <p className="text-gray-400">
                Modern POS solution for retail and restaurant businesses
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#features" className="hover:text-white">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="hover:text-white">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#solutions" className="hover:text-white">
                    Solutions
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white">
                    About Us
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#contact" className="hover:text-white">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-400">
                <li>support@ngpos.com</li>
                <li>+1 (555) 123-4567</li>
                <li>123 Business St, Suite 100</li>
                <li>New York, NY 10001</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2025 NGPOS. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
