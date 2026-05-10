import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowRight, 
  Users, 
  Target, 
  Star, 
  Globe, 
  Shield,
  Zap,
  TrendingUp,
  MessageSquare
} from 'lucide-react';

const Landing = () => {
  const features = [
    {
      icon: Users,
      title: 'Skill Matching',
      description: 'Get matched with people who have the skills you need and want what you offer'
    },
    {
      icon: Globe,
      title: 'Location Based',
      description: 'Find skilled people near you for in-person meetups or online sessions'
    },
    {
      icon: Star,
      title: 'Rating System',
      description: 'Build trust with our community-driven rating and review system'
    },
    {
      icon: Shield,
      title: 'Secure Platform',
      description: 'Your safety and privacy are our top priorities'
    },
    {
      icon: Zap,
      title: 'Real-time Chat',
      description: 'Instant messaging with typing indicators and read receipts'
    },
    {
      icon: TrendingUp,
      title: 'Track Progress',
      description: 'Monitor your skill exchanges and build your reputation'
    }
  ];

  const stats = [
    { value: '10,000+', label: 'Active Users' },
    { value: '50,000+', label: 'Skills Exchanged' },
    { value: '4.8/5', label: 'Average Rating' },
    { value: '120+', label: 'Countries' }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Web Developer',
      content: 'SkillTrade helped me learn guitar while teaching coding. Perfect skill exchange!',
      avatar: '/api/placeholder/40/40'
    },
    {
      name: 'Mike Rodriguez',
      role: 'Photographer',
      content: 'Found amazing yoga instructor who wanted photography lessons. Win-win!',
      avatar: '/api/placeholder/40/40'
    },
    {
      name: 'Emma Thompson',
      role: 'Marketing Expert',
      content: 'The matching algorithm is incredible. Found perfect language exchange partner.',
      avatar: '/api/placeholder/40/40'
    }
  ];

  return (
    <div className="min-h-screen bg-primary">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl lg:text-7xl font-bold text-white mb-6">
              Trade Skills,
              <br />
              <span className="gradient-text">Not Money</span>
            </h1>
            <p className="text-xl lg:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Connect with skilled individuals in your area. Exchange what you know for what you want to learn. 
              Build your network while growing your abilities.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center justify-center px-8 py-4 glass-morphism text-white font-semibold rounded-lg hover:bg-gray-800 transition-all"
              >
                Learn More
              </Link>
            </div>
          </motion.div>

          {/* Floating Elements */}
          <div className="absolute top-20 left-10 w-20 h-20 bg-primary/20 rounded-full animate-float"></div>
          <div className="absolute bottom-20 right-10 w-32 h-32 bg-secondary/20 rounded-full animate-float" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-40 right-20 w-16 h-16 bg-primary/10 rounded-full animate-float" style={{ animationDelay: '2s' }}></div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 glass-morphism border-y border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl lg:text-4xl font-bold gradient-text mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">
              Why Choose SkillTrade?
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our platform makes skill exchange simple, safe, and rewarding for everyone involved.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-morphism p-8 rounded-xl hover-glow"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center mb-6">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                  <p className="text-gray-400">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 glass-morphism border-y border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">
              Loved by Our Community
            </h2>
            <p className="text-xl text-gray-300">
              See what our users are saying about their skill exchange experiences
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-morphism p-8 rounded-xl"
              >
                <div className="flex items-center mb-4">
                  <img 
                    src={testimonial.avatar} 
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <div className="font-semibold text-white">{testimonial.name}</div>
                    <div className="text-gray-400 text-sm">{testimonial.role}</div>
                  </div>
                </div>
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-300 italic">"{testimonial.content}"</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="glass-morphism p-12 rounded-2xl border border-gray-700"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Start Trading Skills?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of people already exchanging skills and growing together.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              Get Started Now
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
