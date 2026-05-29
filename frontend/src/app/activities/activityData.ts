export interface Activity {
  id: string;
  title: string;
  category: 'Recommended' | 'Adventure' | 'Food & Workshops' | 'Family' | 'Hidden Gems' | 'Nightlife';
  rating: number;
  duration: string;
  price: number;
  location: string;
  description: string;
  gradient: string;
  imageUrl: string;
}

export const activitiesData: Record<string, Activity[]> = {
  Goa: [
    {
      id: 'goa-rec-1',
      title: 'Sunset Yacht Cruise in Mandovi',
      category: 'Recommended',
      rating: 4.9,
      duration: '3 hours',
      price: 2500,
      location: 'Panaji',
      description: 'Sail along the serene Mandovi River with live music, local drinks, and spectacular sunset views over the Arabian Sea.',
      gradient: 'from-teal-500/20 to-indigo-500/20 border-teal-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'goa-adv-1',
      title: 'Scuba Diving at Grande Island',
      category: 'Adventure',
      rating: 4.7,
      duration: '6 hours',
      price: 3500,
      location: 'Grande Island',
      description: 'Explore the vibrant underwater marine life, historic shipwrecks, and beautiful coral reefs with certified diving instructors.',
      gradient: 'from-rose-500/20 to-orange-500/20 border-rose-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'goa-food-1',
      title: 'Spice Plantation Tour & Goan Lunch',
      category: 'Food & Workshops',
      rating: 4.8,
      duration: '4 hours',
      price: 1200,
      location: 'Ponda Spice Farm',
      description: 'A sensory walk through aromatic spice fields, followed by a traditional buffet lunch served on fresh banana leaves.',
      gradient: 'from-amber-500/20 to-red-500/20 border-amber-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'goa-fam-1',
      title: 'Dudhsagar Waterfalls Jeep Safari',
      category: 'Family',
      rating: 4.6,
      duration: '8 hours',
      price: 1800,
      location: 'Mollem National Park',
      description: 'Take an exciting off-road jeep safari through dense jungle trails to witness the majestic four-tiered milky waterfall.',
      gradient: 'from-sky-500/20 to-emerald-500/20 border-sky-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'goa-gem-1',
      title: 'Fontainhas Latin Quarter Walking Tour',
      category: 'Hidden Gems',
      rating: 4.9,
      duration: '2 hours',
      price: 800,
      location: 'Panaji Heritage Zone',
      description: 'Stroll past pastel-colored Portuguese villas, ornate wooden balconies, and local art cafes in India\'s only Latin Quarter.',
      gradient: 'from-purple-500/20 to-pink-500/20 border-purple-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'goa-night-1',
      title: 'Beach Bonfire & Fire Show at Curlies',
      category: 'Nightlife',
      rating: 4.5,
      duration: '5 hours',
      price: 1500,
      location: 'Anjuna Beach',
      description: 'Enjoy beachside dining, pulsing international DJ sets, tropical cocktails, and a captivating fire dance performance.',
      gradient: 'from-indigo-600/20 to-purple-600/20 border-indigo-500/25',
      imageUrl: 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&w=600&q=80'
    }
  ],
  Bangalore: [
    {
      id: 'blr-rec-1',
      title: 'Nandi Hills Sunrise Trek',
      category: 'Recommended',
      rating: 4.8,
      duration: '5 hours',
      price: 1200,
      location: 'Chikkaballapur',
      description: 'Hike up the historic hill fortress to witness a breathtaking sunrise above a panoramic sea of clouds.',
      gradient: 'from-teal-500/20 to-indigo-500/20 border-teal-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'blr-adv-1',
      title: 'Go-Karting & Quad Biking Arena',
      category: 'Adventure',
      rating: 4.6,
      duration: '2 hours',
      price: 1000,
      location: 'Sarjapur',
      description: 'Race your friends on a professional twin-track setup and conquer muddy obstacles on 200cc ATVs.',
      gradient: 'from-rose-500/20 to-orange-500/20 border-rose-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'blr-food-1',
      title: 'Microbrewery Trail & Beer Tasting',
      category: 'Food & Workshops',
      rating: 4.9,
      duration: '3 hours',
      price: 1800,
      location: 'Indiranagar',
      description: 'Sample award-winning IPAs and stouts on a guided craft beer crawl across the microbrewery capital of India.',
      gradient: 'from-amber-500/20 to-red-500/20 border-amber-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1571613316887-6f8d5cbf7ef7?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'blr-fam-1',
      title: 'Bannerghatta Tiger & Lion Safari',
      category: 'Family',
      rating: 4.7,
      duration: '4 hours',
      price: 1100,
      location: 'Bannerghatta National Park',
      description: 'Embark on a secure bus safari inside natural forest enclosures to spot Royal Bengal tigers, Asiatic lions, and bears.',
      gradient: 'from-sky-500/20 to-emerald-500/20 border-sky-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1561731216-c3a4d99437d5?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'blr-gem-1',
      title: 'Artisanal Silk Weaving Workshop',
      category: 'Hidden Gems',
      rating: 4.8,
      duration: '3 hours',
      price: 1500,
      location: 'Malleswaram',
      description: 'Go inside local workshops to watch master weavers spin raw silk yarn on complex traditional wooden handlooms.',
      gradient: 'from-purple-500/20 to-pink-500/20 border-purple-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1558244661-d248897f7bc4?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'blr-night-1',
      title: 'Live Jazz & Gastropub Dining',
      category: 'Nightlife',
      rating: 4.9,
      duration: '4 hours',
      price: 2200,
      location: 'Whitefield',
      description: 'Indulge in global fusion cuisine, draft microbrews, and high-fidelity live jazz performances in a curated library-like setting.',
      gradient: 'from-indigo-600/20 to-purple-600/20 border-indigo-500/25',
      imageUrl: 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=600&q=80'
    }
  ],
  Srinagar: [
    {
      id: 'sri-rec-1',
      title: 'Floating Market Shikara Tour',
      category: 'Recommended',
      rating: 4.9,
      duration: '2 hours',
      price: 800,
      location: 'Dal Lake',
      description: 'Wake up early to glide in a wooden shikara boat past floating gardens and watch the historic vegetable market trade.',
      gradient: 'from-teal-500/20 to-indigo-500/20 border-teal-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1566228015668-4c45dbc4e2f5?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'sri-adv-1',
      title: 'Paragliding over Astanmarg Hills',
      category: 'Adventure',
      rating: 4.8,
      duration: '1.5 hours',
      price: 3200,
      location: 'Harwan Range',
      description: 'Fly tandem over alpine forests and village orchards with panoramic views of Dal Lake and the Zabarwan Mountains.',
      gradient: 'from-rose-500/20 to-orange-500/20 border-rose-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1596838132731-3301c3fd4317?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'sri-food-1',
      title: 'Traditional Kashmiri Wazwan Feast',
      category: 'Food & Workshops',
      rating: 4.9,
      duration: '2.5 hours',
      price: 2000,
      location: 'Lal Chowk Area',
      description: 'Sit in traditional arrangements and savor a rich, multi-course ceremonial meal cooked overnight by master wazas.',
      gradient: 'from-amber-500/20 to-red-500/20 border-amber-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'sri-fam-1',
      title: 'Mughal Gardens Heritage Walk',
      category: 'Family',
      rating: 4.7,
      duration: '3 hours',
      price: 600,
      location: 'Shalimar & Nishat Bagh',
      description: 'Explore the beautifully terraced lawns, mountain springs, and historical Persian water channels from the Mughal era.',
      gradient: 'from-sky-500/20 to-emerald-500/20 border-sky-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1465146633011-14f8e0781093?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'sri-gem-1',
      title: 'Old Town Copperware Workshop',
      category: 'Hidden Gems',
      rating: 4.6,
      duration: '3 hours',
      price: 900,
      location: 'Zaina Kadal',
      description: 'Sit with local copper smiths in historical neighborhoods to learn how intricate floral patterns are hand-engraved onto vessels.',
      gradient: 'from-purple-500/20 to-pink-500/20 border-purple-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1605557626697-2e87166a88f9?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'sri-night-1',
      title: 'Houseboat Deck Candlelit Dinner',
      category: 'Nightlife',
      rating: 4.8,
      duration: '3 hours',
      price: 2500,
      location: 'Nigeen Lake',
      description: 'A quiet, exclusive candlelight dinner served on the cedar wood deck of a classic houseboat under a starry night sky.',
      gradient: 'from-indigo-600/20 to-purple-600/20 border-indigo-500/25',
      imageUrl: 'https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?auto=format&fit=crop&w=600&q=80'
    }
  ],
  Jaipur: [
    {
      id: 'jai-rec-1',
      title: 'Amer Fort Guided Jeep Tour',
      category: 'Recommended',
      rating: 4.8,
      duration: '4 hours',
      price: 1500,
      location: 'Amer Hill',
      description: 'Ride up to the grand fortress gates and explore the mirror palace (Sheesh Mahal) and historical royal halls with a historian.',
      gradient: 'from-teal-500/20 to-indigo-500/20 border-teal-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1477587458883-471a5ed94245?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'jai-adv-1',
      title: 'Sunrise Hot Air Balloon Flight',
      category: 'Adventure',
      rating: 4.9,
      duration: '3 hours',
      price: 8500,
      location: 'Kukas Valley',
      description: 'Float high above pink palaces, sandy gorges, and small villages as the morning sun illuminates the Rajasthan landscape.',
      gradient: 'from-rose-500/20 to-orange-500/20 border-rose-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'jai-food-1',
      title: 'Block Printing Masterclass',
      category: 'Food & Workshops',
      rating: 4.7,
      duration: '3 hours',
      price: 1300,
      location: 'Sanganer Village',
      description: 'Learn the wooden block-printing technique from heritage artisans and print your own custom design on organic cotton fabric.',
      gradient: 'from-amber-500/20 to-red-500/20 border-amber-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1595079676339-1534801ad6cf?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'jai-fam-1',
      title: 'Chokhi Dhani Cultural Feast',
      category: 'Family',
      rating: 4.6,
      duration: '5 hours',
      price: 1200,
      location: 'Tonk Road',
      description: 'Immerse in folk dances, puppet plays, camel rides, and an authentic multi-course sit-down Rajasthani feast.',
      gradient: 'from-sky-500/20 to-emerald-500/20 border-sky-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1582560475093-ba66accbc424?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'jai-gem-1',
      title: 'Astronomy & Sunset at Panna Meena',
      category: 'Hidden Gems',
      rating: 4.8,
      duration: '2 hours',
      price: 700,
      location: 'Amer Stepwell',
      description: 'Discover the structural mathematics of the ancient stepwell and hear astronomical tales as the sunset glows on the step arches.',
      gradient: 'from-purple-500/20 to-pink-500/20 border-purple-500/20',
      imageUrl: 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'jai-night-1',
      title: 'Nahargarh Fort Light & Sunset Dinner',
      category: 'Nightlife',
      rating: 4.7,
      duration: '4 hours',
      price: 2000,
      location: 'Nahargarh Summit',
      description: 'Watch the illuminated Pink City night views from the summit fortress restaurant while enjoying royal Rajasthani curries.',
      gradient: 'from-indigo-600/20 to-purple-600/20 border-indigo-500/25',
      imageUrl: 'https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80'
    }
  ]
};
