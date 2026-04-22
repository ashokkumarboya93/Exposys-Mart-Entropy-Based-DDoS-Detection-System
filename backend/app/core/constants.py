"""
Application Constants
----------------------
Product catalog, attack presets, and detection parameters.
"""

from __future__ import annotations


class TrafficConstants:
    NORMAL_IP_POOL_MIN: int = 20
    NORMAL_IP_POOL_MAX: int = 50
    NORMAL_REQUESTS_PER_IP_MIN: int = 1
    NORMAL_REQUESTS_PER_IP_MAX: int = 5
    NORMAL_IP_SUBNET: str = "192.168.1"

    ATTACK_IP_POOL_MIN: int = 2
    ATTACK_IP_POOL_MAX: int = 5
    ATTACK_REQUESTS_PER_IP_MIN: int = 100
    ATTACK_REQUESTS_PER_IP_MAX: int = 500
    ATTACK_IP_SUBNET: str = "10.0.0"


class DetectionConstants:
    LOG_BASE: int = 2
    MIN_ENTROPY: float = 0.0
    MAX_ENTROPY_LABEL: str = "high"
    LOW_ENTROPY_LABEL: str = "low"
    STATUS_NORMAL: str = "NORMAL"
    STATUS_ATTACK: str = "DDOS_ATTACK"
    STATUS_UNKNOWN: str = "INSUFFICIENT_DATA"
    SEVERITY_SAFE: str = "safe"
    SEVERITY_WARNING: str = "warning"
    SEVERITY_CRITICAL: str = "critical"


class AttackPresets:
    """Pre-configured attack scenarios."""
    PRESETS = {
        "spike": {
            "name": "Traffic Spike",
            "description": "Quick burst of concentrated traffic from few IPs",
            "icon": "🔥",
            "num_ips": 5,
            "requests_per_ip": 500,
            "waves": 1,
            "wave_delay_ms": 0,
        },
        "swarm": {
            "name": "Bot Swarm",
            "description": "Distributed flood from many bot IPs",
            "icon": "🤖",
            "num_ips": 20,
            "requests_per_ip": 200,
            "waves": 3,
            "wave_delay_ms": 500,
        },
        "flood": {
            "name": "Sustained Flood",
            "description": "Heavy sustained load from few dedicated IPs",
            "icon": "🌊",
            "num_ips": 3,
            "requests_per_ip": 2000,
            "waves": 5,
            "wave_delay_ms": 800,
        },
        "checkout_flood": {
            "name": "Checkout Flood",
            "description": "High volume of requests attempting to exhaust checkout infrastructure.",
            "icon": "🛒",
            "num_ips": 10,
            "requests_per_ip": 1500,
            "waves": 2,
            "wave_delay_ms": 300,
        },
        "product_burst": {
            "name": "Product Page Burst",
            "description": "Targeted burst against random product detail pages to exhaust database reads.",
            "icon": "🎯",
            "num_ips": 15,
            "requests_per_ip": 400,
            "waves": 4,
            "wave_delay_ms": 600,
        },
    }


PRODUCT_CATALOG = [
    # ── Electronics (10 items) ────────────────────────────────────────────
    {
        "id": 1, "name": "MacBook Air M2 Laptop", "brand": "Apple", "price": 69990.0, "original_price": 99900.0, "category": "electronics", "rating": 4.8, "reviews": 12834, "badge": "Bestseller", "image": "/store/images/products/1.jpg", "description": "Apple M2 chip, 13.6-inch Liquid Retina display, 8GB RAM, 256GB SSD.", "specs": {"Chip": "Apple M2", "RAM": "8GB Unified", "Storage": "256GB SSD", "Display": "13.6\" Liquid Retina"}
    },
    {
        "id": 2, "name": "Samsung Galaxy S24 Ultra", "brand": "Samsung", "price": 109999.0, "original_price": 129999.0, "category": "electronics", "rating": 4.7, "reviews": 8621, "badge": "New", "image": "/store/images/products/2.jpg", "description": "6.8-inch Dynamic AMOLED 2X, 200MP camera, Galaxy AI powered.", "specs": {"Display": "6.8\" QHD+ AMOLED", "Camera": "200MP Quad", "Battery": "5000mAh", "Storage": "256GB"}
    },
    {
        "id": 3, "name": "Sony WH-1000XM5 Headphones", "brand": "Sony", "price": 22990.0, "original_price": 34990.0, "category": "electronics", "rating": 4.8, "reviews": 15203, "badge": "Deal", "image": "/store/images/products/3.jpg", "description": "Industry-leading noise cancellation, 30-hour battery.", "specs": {"Driver": "30mm Dynamic", "ANC": "Auto NC Optimizer", "Battery": "30 hours", "Bluetooth": "5.2"}
    },
    {
        "id": 4, "name": "Apple Watch Series 9", "brand": "Apple", "price": 32900.0, "original_price": 41900.0, "category": "electronics", "rating": 4.6, "reviews": 9102, "badge": "Premium", "image": "/store/images/products/4.jpg", "description": "Advanced health and fitness tracking, Double Tap gesture.", "specs": {"Display": "Always-On Retina", "Chip": "S9 SiP", "Water": "50m WR", "GPS": "Precision L1+L5"}
    },
    {
        "id": 5, "name": "Canon EOS R6 Mark II", "brand": "Canon", "price": 215000.0, "original_price": 243995.0, "category": "electronics", "rating": 4.9, "reviews": 3892, "badge": "Pro", "image": "/store/images/products/5.jpg", "description": "24.2MP Full-Frame CMOS, 4K 60p video, up to 40fps.", "specs": {"Sensor": "24.2MP Full-Frame", "Video": "4K 60fps", "ISO": "100-102400", "AF Points": "1053"}
    },
    {
        "id": 6, "name": "iPad Pro 12.9\" M2", "brand": "Apple", "price": 95900.0, "original_price": 112900.0, "category": "electronics", "rating": 4.7, "reviews": 6156, "badge": "Hot", "image": "/store/images/products/6.jpg", "description": "12.9-inch Liquid Retina XDR, M2 chip, ProRes video.", "specs": {"Display": "12.9\" XDR", "Chip": "Apple M2", "Storage": "256GB", "Pencil": "2nd Gen Support"}
    },
    {
        "id": 10, "name": "Logitech MX Keys S Keyboard", "brand": "Logitech", "price": 9990.0, "original_price": 12995.0, "category": "electronics", "rating": 4.6, "reviews": 4678, "badge": "Editor Pick", "image": "/store/images/products/10.jpg", "description": "Smart illumination, programmable keys, multi-device pairing.", "specs": {"Type": "Low-profile Keys", "Backlight": "Smart Illumination", "Connect": "BT + USB", "Battery": "10 days"}
    },
    {
        "id": 11, "name": "JBL Charge 5 Speaker", "brand": "JBL", "price": 11999.0, "original_price": 14999.0, "category": "electronics", "rating": 4.7, "reviews": 18432, "badge": "Top Rated", "image": "/store/images/products/11.jpg", "description": "Portable Bluetooth speaker with 20-hour playtime, IP67 waterproof.", "specs": {"Power": "40W", "Battery": "20 hours", "Bluetooth": "5.1", "Protection": "IP67"}
    },
    {
        "id": 12, "name": "Logitech MX Master 3S Mouse", "brand": "Logitech", "price": 8495.0, "original_price": 10495.0, "category": "electronics", "rating": 4.8, "reviews": 11287, "badge": "Ergonomic", "image": "/store/images/products/12.jpg", "description": "Advanced ergonomic wireless mouse, 8000 DPI track-on-glass sensor.", "specs": {"DPI": "8000", "Battery": "70 days", "Connect": "BT + USB-C", "Buttons": "7"}
    },
    {
        "id": 101, "name": "Nintendo Switch OLED", "brand": "Nintendo", "price": 26990.0, "original_price": 34990.0, "category": "electronics", "rating": 4.9, "reviews": 32001, "badge": "Console", "image": "/store/images/products/101.jpg", "description": "Play at home or on the go with a vibrant 7-inch OLED screen.", "specs": {"Screen": "7\" OLED", "Storage": "64GB", "Battery": "4.5-9 hours", "Weight": "420g"}
    },
    {
        "id": 102, "name": "Kindle Paperwhite", "brand": "Amazon", "price": 10999.0, "original_price": 13999.0, "category": "electronics", "rating": 4.8, "reviews": 65412, "badge": "E-Reader", "image": "/store/images/products/102.jpg", "description": "Now with a 6.8\" display and adjustable warm light. Waterproof.", "specs": {"Display": "6.8\" Glare-free", "Storage": "16GB", "Battery": "10 weeks", "Waterproof": "IPX8"}
    },

    # ── Fashion (10 items) ────────────────────────────────────────────────
    {
        "id": 7, "name": "Nike Air Max 270 React", "brand": "Nike", "price": 8995.0, "original_price": 13995.0, "category": "fashion", "rating": 4.5, "reviews": 24521, "badge": "Trending", "image": "/store/images/products/7.jpg", "description": "Nike React foam with Max Air 270 unit, breathable mesh upper.", "specs": {"Weight": "285g", "Cushioning": "React + Air Max", "Upper": "Engineered Mesh", "Sole": "Rubber Outsole"}
    },
    {
        "id": 8, "name": "Ray-Ban Aviator Classic", "brand": "Ray-Ban", "price": 6590.0, "original_price": 9590.0, "category": "fashion", "rating": 4.7, "reviews": 31876, "badge": "Iconic", "image": "/store/images/products/8.jpg", "description": "Original aviator sunglasses with polarized crystal green lenses.", "specs": {"Lens": "Polarized Crystal Green", "Frame": "Gold Metal", "UV": "UV400", "Size": "58mm"}
    },
    {
        "id": 9, "name": "Herschel Retreat Backpack", "brand": "Herschel", "price": 4500.0, "original_price": 8500.0, "category": "fashion", "rating": 4.6, "reviews": 8245, "badge": "Popular", "image": "/store/images/products/9.jpg", "description": "Classic silhouette backpack with padded 15\" laptop sleeve.", "specs": {"Capacity": "19.5L", "Material": "600D Polyester", "Laptop": "Up to 15\"", "Straps": "Vegan Leather"}
    },
    {
        "id": 17, "name": "Levi's 501 Original Fit Jeans", "brand": "Levi's", "price": 2599.0, "original_price": 4599.0, "category": "fashion", "rating": 4.5, "reviews": 42156, "badge": "Classic", "image": "/store/images/products/17.jpg", "description": "The original button fly jean, straight leg fit, 100% cotton denim.", "specs": {"Fit": "Original Straight", "Material": "100% Cotton", "Rise": "Regular", "Leg": "Straight"}
    },
    {
        "id": 18, "name": "Casio G-Shock GA-2100", "brand": "Casio", "price": 6995.0, "original_price": 8995.0, "category": "fashion", "rating": 4.7, "reviews": 15678, "badge": "Tough", "image": "/store/images/products/18.jpg", "description": "Octagonal bezel, carbon core guard structure, 200m water resistance.", "specs": {"Movement": "Quartz Analog-Digital", "Water": "200m", "Battery": "3 years", "Weight": "51g"}
    },
    {
        "id": 103, "name": "Adidas Ultraboost 1.0", "brand": "Adidas", "price": 8999.0, "original_price": 17999.0, "category": "fashion", "rating": 4.8, "reviews": 14500, "badge": "Running", "image": "/store/images/products/103.jpg", "description": "Responsive running shoes with Primeknit upper.", "specs": {"Upper": "Primeknit", "Midsole": "Boost", "Drop": "10mm", "Weight": "328g"}
    },
    {
        "id": 104, "name": "The North Face Nuptse Jacket", "brand": "The North Face", "price": 15000.0, "original_price": 30000.0, "category": "fashion", "rating": 4.9, "reviews": 8900, "badge": "Winter", "image": "/store/images/products/104.jpg", "description": "Iconic puffer jacket with 700-fill goose down insulation.", "specs": {"Insulation": "700-fill down", "Fit": "Relaxed", "Weight": "775g", "Material": "Ripstop nylon"}
    },
    {
        "id": 105, "name": "Patagonia Better Sweater", "brand": "Patagonia", "price": 6000.0, "original_price": 12000.0, "category": "fashion", "rating": 4.8, "reviews": 12300, "badge": "Fleece", "image": "/store/images/products/105.jpg", "description": "Warm, 100% recycled polyester quarter-zip fleece.", "specs": {"Material": "100% Recycled Fleece", "Fit": "Regular", "Weight": "505g", "Fair Trade": "Certified"}
    },
    {
        "id": 106, "name": "Timberland Premium 6-Inch Boot", "brand": "Timberland", "price": 9990.0, "original_price": 16990.0, "category": "fashion", "rating": 4.7, "reviews": 18200, "badge": "Iconic", "image": "/store/images/products/106.jpg", "description": "The original waterproof work boot.", "specs": {"Upper": "Nubuck Leather", "Waterproof": "Seam-sealed", "Insulation": "400g PrimaLoft", "Outsole": "Rubber Lug"}
    },
    {
        "id": 107, "name": "Vans Old Skool Sneakers", "brand": "Vans", "price": 3499.0, "original_price": 5999.0, "category": "fashion", "rating": 4.6, "reviews": 34000, "badge": "Skate", "image": "/store/images/products/107.jpg", "description": "Classic low-top skate shoe with the iconic side stripe.", "specs": {"Upper": "Suede and Canvas", "Sole": "Waffle Rubber", "Collar": "Padded", "Closure": "Lace-up"}
    },

    # ── Books (10 items) ──────────────────────────────────────────────────
    {
        "id": 13, "name": "Atomic Habits by James Clear", "brand": "Penguin Random House", "price": 250.0, "original_price": 500.0, "category": "books", "rating": 4.9, "reviews": 128543, "badge": "#1 Best", "image": "/store/images/products/13.jpg", "description": "An easy & proven way to build good habits & break bad ones.", "specs": {"Pages": "320", "Format": "Hardcover", "Language": "English", "Publisher": "Penguin Random House"}
    },
    {
        "id": 19, "name": "Clean Code by Robert C. Martin", "brand": "Pearson Education", "price": 550.0, "original_price": 900.0, "category": "books", "rating": 4.7, "reviews": 18921, "badge": "Dev Essential", "image": "/store/images/products/19.jpg", "description": "A handbook of agile software craftsmanship.", "specs": {"Pages": "464", "Format": "Paperback", "Language": "English", "Publisher": "Pearson"}
    },
    {
        "id": 20, "name": "The Psychology of Money", "brand": "Harriman House", "price": 180.0, "original_price": 350.0, "category": "books", "rating": 4.8, "reviews": 85432, "badge": "Bestseller", "image": "/store/images/products/20.jpg", "description": "Timeless lessons on wealth, greed, and happiness.", "specs": {"Pages": "256", "Format": "Paperback", "Language": "English", "Publisher": "Harriman House"}
    },
    {
        "id": 108, "name": "Sapiens: A Brief History of Humankind", "brand": "Harper", "price": 220.0, "original_price": 450.0, "category": "books", "rating": 4.8, "reviews": 65000, "badge": "History", "image": "/store/images/products/108.jpg", "description": "Explores the history of the human species.", "specs": {"Pages": "464", "Format": "Paperback", "Language": "English", "Publisher": "Harper"}
    },
    {
        "id": 109, "name": "Dune by Frank Herbert", "brand": "Ace", "price": 350.0, "original_price": 550.0, "category": "books", "rating": 4.7, "reviews": 42000, "badge": "Sci-Fi", "image": "/store/images/products/109.jpg", "description": "The epic science fiction masterpiece.", "specs": {"Pages": "896", "Format": "Paperback", "Language": "English", "Publisher": "Ace"}
    },
    {
        "id": 110, "name": "Thinking, Fast and Slow", "brand": "FSG", "price": 280.0, "original_price": 450.0, "category": "books", "rating": 4.6, "reviews": 31000, "badge": "Psychology", "image": "/store/images/products/110.jpg", "description": "A tour of the mind and the two systems that drive the way we think.", "specs": {"Pages": "512", "Format": "Paperback", "Language": "English", "Publisher": "Farrar, Straus and Giroux"}
    },
    {
        "id": 111, "name": "The Pragmatic Programmer", "brand": "Addison-Wesley", "price": 1800.0, "original_price": 3500.0, "category": "books", "rating": 4.8, "reviews": 11000, "badge": "Tech", "image": "/store/images/products/111.jpg", "description": "Your journey to mastery in software development.", "specs": {"Pages": "352", "Format": "Hardcover", "Language": "English", "Publisher": "Addison-Wesley Professional"}
    },
    {
        "id": 112, "name": "Project Hail Mary", "brand": "Ballantine Books", "price": 350.0, "original_price": 600.0, "category": "books", "rating": 4.9, "reviews": 75000, "badge": "Sci-Fi", "image": "/store/images/products/112.jpg", "description": "A lone astronaut must save the earth from disaster.", "specs": {"Pages": "496", "Format": "Hardcover", "Language": "English", "Publisher": "Ballantine Books"}
    },
    {
        "id": 113, "name": "Design Patterns", "brand": "Addison-Wesley", "price": 1500.0, "original_price": 3000.0, "category": "books", "rating": 4.7, "reviews": 8500, "badge": "CS Classic", "image": "/store/images/products/113.jpg", "description": "Elements of Reusable Object-Oriented Software.", "specs": {"Pages": "416", "Format": "Hardcover", "Language": "English", "Publisher": "Addison-Wesley Professional"}
    },
    {
        "id": 114, "name": "The Alchemist", "brand": "HarperOne", "price": 150.0, "original_price": 250.0, "category": "books", "rating": 4.7, "reviews": 120000, "badge": "Fiction", "image": "/store/images/products/114.jpg", "description": "A story about following your dreams.", "specs": {"Pages": "208", "Format": "Paperback", "Language": "English", "Publisher": "HarperOne"}
    },

    # ── Home & Living (10 items) ──────────────────────────────────────────
    {
        "id": 14, "name": "Philips Hue White Ambiance Lamp", "brand": "Philips", "price": 1800.0, "original_price": 2500.0, "category": "home", "rating": 4.6, "reviews": 11245, "badge": "Smart Home", "image": "/store/images/products/14.png", "description": "Smart LED lamp with app control.", "specs": {"Light": "LED 9.5W", "Color Temp": "2200-6500K", "Smart": "Zigbee + BT", "Lifespan": "25000 hours"}
    },
    {
        "id": 15, "name": "Fiddle Leaf Fig Indoor Plant", "brand": "The Sill", "price": 600.0, "original_price": 1200.0, "category": "home", "rating": 4.4, "reviews": 4876, "badge": "Trending", "image": "/store/images/products/15.jpg", "description": "Statement indoor plant in premium ceramic planter.", "specs": {"Height": "45-60cm", "Pot": "Ceramic 7\"", "Light": "Bright Indirect", "Water": "Weekly"}
    },
    {
        "id": 16, "name": "Nespresso Vertuo Next Machine", "brand": "Nespresso", "price": 12999.0, "original_price": 18999.0, "category": "home", "rating": 4.5, "reviews": 22134, "badge": "Top Pick", "image": "/store/images/products/16.jpg", "description": "Centrifusion brewing, 5 cup sizes.", "specs": {"Brew": "Centrifusion™", "Cups": "5 sizes (5-535ml)", "Heat-up": "30 seconds", "Tank": "1.1L"}
    },
    {
        "id": 21, "name": "IKEA KALLAX Shelf Unit", "brand": "IKEA", "price": 3500.0, "original_price": 5500.0, "category": "home", "rating": 4.5, "reviews": 34521, "badge": "Popular", "image": "/store/images/products/21.jpg", "description": "Versatile 4x2 cube shelf unit.", "specs": {"Size": "147x77x39cm", "Material": "Particleboard", "Cubes": "8", "Weight": "32kg"}
    },
    {
        "id": 22, "name": "Dyson V15 Detect Vacuum", "brand": "Dyson", "price": 49900.0, "original_price": 65900.0, "category": "home", "rating": 4.8, "reviews": 9876, "badge": "Premium", "image": "/store/images/products/22.jpg", "description": "Laser reveals hidden dust.", "specs": {"Motor": "Hyperdymium™ 125K RPM", "Runtime": "60 min", "Suction": "240AW", "Filter": "HEPA"}
    },
    {
        "id": 115, "name": "Vitamix 5200 Blender", "brand": "Vitamix", "price": 25000.0, "original_price": 45000.0, "category": "home", "rating": 4.9, "reviews": 15000, "badge": "Kitchen Pro", "image": "/store/images/products/115.jpg", "description": "Professional-grade blender for smoothies, soups, and more.", "specs": {"Capacity": "64 oz", "Power": "2.0 HP", "Speeds": "Variable 10-speed", "Warranty": "7 Years"}
    },
    {
        "id": 116, "name": "Le Creuset Dutch Oven", "brand": "Le Creuset", "price": 18000.0, "original_price": 35000.0, "category": "home", "rating": 4.8, "reviews": 8500, "badge": "Cookware", "image": "/store/images/products/116.jpg", "description": "Enameled cast iron signature round Dutch oven.", "specs": {"Capacity": "5.5 qt", "Material": "Cast Iron", "Heat": "Up to 500°F", "Care": "Dishwasher Safe"}
    },
    {
        "id": 117, "name": "Herman Miller Aeron Chair", "brand": "Herman Miller", "price": 85000.0, "original_price": 125000.0, "category": "home", "rating": 4.7, "reviews": 9200, "badge": "Ergonomic", "image": "/store/images/products/117.jpg", "description": "The benchmark for ergonomic office seating.", "specs": {"Material": "8Z Pellicle Mesh", "Adjustability": "Fully Loaded", "Sizes": "A, B, C", "Warranty": "12 Years"}
    },
    {
        "id": 118, "name": "YETI Tundra 45 Cooler", "brand": "YETI", "price": 18000.0, "original_price": 32000.0, "category": "home", "rating": 4.8, "reviews": 11000, "badge": "Outdoor", "image": "/store/images/products/118.jpg", "description": "Extremely durable, heavily insulated hard cooler.", "specs": {"Capacity": "32.9 Liters", "Insulation": "PermaFrost", "Material": "Rotomolded", "Empty Weight": "23 lbs"}
    },
    {
        "id": 119, "name": "Bose Smart Soundbar 900", "brand": "Bose", "price": 79900.0, "original_price": 104900.0, "category": "home", "rating": 4.6, "reviews": 5600, "badge": "Audio", "image": "/store/images/products/119.jpg", "description": "Dolby Atmos soundbar with voice assistants built-in.", "specs": {"Channels": "5.0.2", "Audio": "Dolby Atmos", "Connect": "HDMI eARC, Wi-Fi, BT", "Voice": "Alexa, Google"}
    },
    {
        "id": 120, "name": "Amazon Echo Dot (5th Gen)", "brand": "Amazon", "price": 4499.0, "original_price": 5499.0, "category": "electronics", "rating": 4.7, "reviews": 25400, "badge": "Smart Speaker", "image": "https://images.unsplash.com/photo-1589492477829-5e65395b66cc?w=500&h=500&fit=crop", "description": "Our best-sounding Echo Dot yet. Enjoy an improved audio experience.", "specs": {"Speaker": "1.73\" Front-firing", "Voice": "Alexa Built-in", "Motion": "Detection", "Temp": "Sensor"}
    },
    {
        "id": 121, "name": "Sony PlayStation 5 Console", "brand": "Sony", "price": 54990.0, "original_price": 54990.0, "category": "electronics", "rating": 4.9, "reviews": 12500, "badge": "Console", "image": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500&h=500&fit=crop", "description": "Experience lightning-fast loading with an ultra-high speed SSD.", "specs": {"CPU": "8-core AMD Ryzen Zen 2", "GPU": "AMD Radeon RDNA 2", "Storage": "825GB SSD", "Video": "4K 120fps"}
    },
    {
        "id": 122, "name": "Instant Pot Duo 7-in-1", "brand": "Instant Pot", "price": 8999.0, "original_price": 12999.0, "category": "home", "rating": 4.7, "reviews": 156000, "badge": "Kitchen Pick", "image": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=500&h=500&fit=crop", "description": "Cooks fast and saves time. The #1 selling multi-cooker.", "specs": {"Functions": "7-in-1", "Safety": "10+ Features", "Capacity": "6 Quart", "Material": "Stainless Steel"}
    },
    {
        "id": 123, "name": "Apple AirPods Pro (2nd Gen)", "brand": "Apple", "price": 24900.0, "original_price": 26900.0, "category": "electronics", "rating": 4.8, "reviews": 45200, "badge": "Premium", "image": "https://images.unsplash.com/photo-1588423770574-91093b707971?w=500&h=500&fit=crop", "description": "Up to 2x more Active Noise Cancellation. Transparency mode.", "specs": {"Chip": "H2 Chip", "ANC": "Adaptive Audio", "Battery": "6 hours", "Charging": "MagSafe / USB-C"}
    },
    {
        "id": 124, "name": "Fire TV Stick 4K", "brand": "Amazon", "price": 3999.0, "original_price": 5999.0, "category": "electronics", "rating": 4.7, "reviews": 89000, "badge": "Streaming", "image": "https://images.unsplash.com/photo-1544244015-0cd4b3ff6f70?w=500&h=500&fit=crop", "description": "Cinematic experience in 4K with support for Dolby Vision, HDR, and HDR10+.", "specs": {"Quality": "4K Ultra HD", "Remote": "Alexa Voice Remote", "Apps": "Netlfix, Prime, etc.", "Audio": "Dolby Atmos"}
    }

]

CATEGORIES = [
    {"id": "all", "name": "All", "icon": "grid"},
    {"id": "electronics", "name": "Electronics", "icon": "monitor"},
    {"id": "fashion", "name": "Fashion", "icon": "shirt"},
    {"id": "home", "name": "Home & Living", "icon": "home"},
    {"id": "books", "name": "Books", "icon": "book"},
]
