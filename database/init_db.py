"""
One-time database initialiser + seeder.
Run: python database/init_db.py
Creates roadsos.db with schema + seeds Tier 1 national numbers
+ Tier 2 verified contacts for major cities and NH corridors.
"""

import sqlite3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DB_PATH   = os.environ.get("ROADSOS_DB", "roadsos.db")
SCHEMA    = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA) as f:
        conn.executescript(f.read())
    conn.commit()
    print("[DB] Schema created: " + DB_PATH)
    return conn


def seed_national_numbers(conn):
    numbers = [
        ("IN","India",       "100","108","101","112","112=all; 108=ambulance NHM; 1033=NHAI"),
        ("US","USA",         "911","911","911","911",None),
        ("GB","UK",          "999","999","999","999",None),
        ("AU","Australia",   "000","000","000","000",None),
        ("DE","Germany",     "110","112","112","112",None),
        ("FR","France",      "17", "15", "18", "112",None),
        ("CN","China",       "110","120","119",None,  None),
        ("JP","Japan",       "110","119","119",None,  None),
        ("BR","Brazil",      "190","192","193",None,  None),
        ("ZA","South Africa","10111","10177","10177","112",None),
        ("PK","Pakistan",    "15", "115","16", "1122",None),
        ("BD","Bangladesh",  "999","999","999","999", None),
        ("LK","Sri Lanka",   "119","110","111",None,  None),
        ("NP","Nepal",       "100","102","101",None,  None),
        ("AE","UAE",         "999","998","997","999", None),
        ("SG","Singapore",   "999","995","995",None,  None),
        ("MY","Malaysia",    "999","999","994","999", None),
        ("TH","Thailand",    "191","1669","199","191",None),
        ("ID","Indonesia",   "110","118","113","112", None),
        ("PH","Philippines", "911","911","911","911", None),
        ("CA","Canada",      "911","911","911","911", None),
        ("NZ","New Zealand", "111","111","111","111", None),
        ("KE","Kenya",       "999","999","999","999", None),
        ("EG","Egypt",       "122","123","180",None,  None),
        ("NG","Nigeria",     "199","199","199","199", None),
        ("IT","Italy",       "113","118","115","112", None),
        ("ES","Spain",       "091","112","080","112", None),
        ("PT","Portugal",    "112","112","112","112", None),
        ("NL","Netherlands", "112","112","112","112", None),
        ("SE","Sweden",      "112","112","112","112", None),
        ("NO","Norway",      "112","113","110","112", None),
        ("CH","Switzerland", "117","144","118","112", None),
        ("RU","Russia",      "102","103","101","112", None),
        ("SA","Saudi Arabia","999","997","998","911", None),
        ("MX","Mexico",      "911","911","911","911", None),
        ("AR","Argentina",   "911","107","100","911", None),
        ("CO","Colombia",    "123","125","119","123", None),
        ("KR","South Korea", "112","119","119","119", None),
        ("TR","Turkey",      "155","112","110","112", None),
        ("IL","Israel",      "100","101","102","112", None),
        ("ZW","Zimbabwe",    "999","994","993","999", None),
        ("GH","Ghana",       "191","193","192","999", None),
        ("TZ","Tanzania",    "111","114","115","112", None),
        ("MM","Myanmar",     "199","192","191",None,  None),
        ("VN","Vietnam",     "113","115","114",None,  None),
        ("HK","Hong Kong",   "999","999","999","999", None),
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO national_numbers
        (country_code, country_name, police, ambulance, fire, emergency, notes)
        VALUES (?,?,?,?,?,?,?)
    """, numbers)
    conn.commit()
    print("[DB] Seeded " + str(len(numbers)) + " country emergency numbers.")


def seed_tier2_contacts(conn):
    contacts = [
        ("Government General Hospital Chennai","hospital",2,"044-25305000",None,"Park Town, Chennai",13.0827,80.2707,"Tamil Nadu","Chennai","nhp",88),
        ("Rajiv Gandhi Govt General Hospital Chennai","hospital",2,"044-25384316",None,"Anna Salai, Chennai",13.0736,80.2609,"Tamil Nadu","Chennai","nhp",85),
        ("Coimbatore Government Hospital","hospital",2,"0422-2301945",None,"Trichy Road, Coimbatore",10.9981,76.9533,"Tamil Nadu","Coimbatore","nhp",83),
        ("Madurai Government Rajaji Hospital","hospital",2,"0452-2532535",None,"Panagal Road, Madurai",9.9252,78.1198,"Tamil Nadu","Madurai","nhp",83),
        ("Government Hospital Salem - NH-44","hospital",2,"0427-2411319",None,"Omalur Road, Salem - NH-44 corridor",11.6643,78.1460,"Tamil Nadu","Salem","nhp",82),
        ("Government Hospital Krishnagiri - NH-44","hospital",2,"04343-233246",None,"Hosur Road, Krishnagiri - NH-44/NH-48",12.5186,78.2137,"Tamil Nadu","Krishnagiri","nhp",80),
        ("Government Hospital Vellore - NH-48","hospital",2,"0416-2281800",None,"Adukkamparai, Vellore - NH-48 corridor",12.9165,79.1325,"Tamil Nadu","Vellore","nhp",82),
        ("Government Hospital Trichy","hospital",2,"0431-2704359",None,"Salai Road, Tiruchirappalli",10.8050,78.6856,"Tamil Nadu","Trichy","nhp",82),
        ("Government Hospital Tirunelveli","hospital",2,"0462-2572444",None,"High Ground Road, Tirunelveli",8.7139,77.7567,"Tamil Nadu","Tirunelveli","nhp",81),
        ("Chennai Police Control Room","police",2,"044-28447777",None,"Vepery, Chennai",13.0916,80.2801,"Tamil Nadu","Chennai","state_police_website",87),
        ("Tamil Nadu Highway Patrol","police",2,"044-24673556",None,"Chennai - statewide highway patrol",13.0827,80.2707,"Tamil Nadu","Chennai","state_police_website",85),
        ("Tamil Nadu Ambulance 108","ambulance",1,"108",None,"Tamil Nadu statewide",None,None,"Tamil Nadu",None,"government_mandated",100),
        ("Victoria Hospital Bangalore","hospital",2,"080-26701150",None,"Fort Road, Bengaluru",12.9636,77.5854,"Karnataka","Bengaluru","nhp",85),
        ("Bangalore NIMHANS","hospital",2,"080-46110007",None,"Hosur Road, Bengaluru",12.9401,77.5959,"Karnataka","Bengaluru","nhp",88),
        ("Mysuru Government Hospital","hospital",2,"0821-2418866",None,"Irwin Road, Mysuru",12.2958,76.6394,"Karnataka","Mysuru","nhp",82),
        ("KIMS Hubli - NH-48","hospital",2,"0836-2375777",None,"Vidyanagar, Hubli - NH-48 corridor",15.3647,75.1240,"Karnataka","Hubli","nhp",83),
        ("Government Hospital Dharwad - NH-48","hospital",2,"0836-2747110",None,"PB Road, Dharwad - NH-48",15.4589,75.0078,"Karnataka","Dharwad","nhp",81),
        ("Government Hospital Belagavi - NH-48","hospital",2,"0831-2405170",None,"Ashok Nagar, Belagavi - NH-48",15.8497,74.4977,"Karnataka","Belagavi","nhp",81),
        ("Government Hospital Tumkur - NH-48","hospital",2,"0816-2272066",None,"B.H. Road, Tumkur - NH-48 corridor",13.3409,77.1010,"Karnataka","Tumkur","nhp",80),
        ("Government Hospital Mangaluru - NH-66","hospital",2,"0824-2220461",None,"Lighthouse Hill Rd, Mangaluru - NH-66",12.8698,74.8431,"Karnataka","Mangaluru","nhp",82),
        ("Government Hospital Shivamogga","hospital",2,"08182-222350",None,"Shivamogga - NH-169",13.9299,75.5681,"Karnataka","Shivamogga","nhp",80),
        ("Bangalore Police Control Room","police",2,"080-22943030",None,"Infantry Road, Bengaluru",12.9791,77.6010,"Karnataka","Bengaluru","state_police_website",87),
        ("Karnataka Highway Police","police",2,"1033","080-22943030","Karnataka highway patrol statewide",12.9716,77.5946,"Karnataka","Bengaluru","state_police_website",85),
        ("Karnataka Ambulance 108","ambulance",1,"108",None,"Karnataka statewide",None,None,"Karnataka",None,"government_mandated",100),
        ("KEM Hospital Mumbai","hospital",2,"022-24107000",None,"Parel, Mumbai",19.0035,72.8407,"Maharashtra","Mumbai","nhp",88),
        ("JJ Hospital Mumbai","hospital",2,"022-23735555",None,"Byculla, Mumbai",18.9716,72.8355,"Maharashtra","Mumbai","nhp",87),
        ("Sassoon General Hospital Pune","hospital",2,"020-26128000",None,"Pune Station Road, Pune",18.5241,73.8749,"Maharashtra","Pune","nhp",85),
        ("Government Hospital Nashik - NH-60","hospital",2,"0253-2573160",None,"Nashik Road, Nashik - NH-60",19.9975,73.7898,"Maharashtra","Nashik","nhp",81),
        ("Government Medical College Nagpur - NH-44","hospital",2,"0712-2745011",None,"Hanuman Nagar, Nagpur - NH-44",21.1458,79.0882,"Maharashtra","Nagpur","nhp",85),
        ("Government Hospital Aurangabad","hospital",2,"0240-2334442",None,"Ghati, Aurangabad",19.8762,75.3433,"Maharashtra","Aurangabad","nhp",82),
        ("Civil Hospital Solapur - NH-52","hospital",2,"0217-2620155",None,"Vijapur Road, Solapur - NH-52",17.6599,75.9064,"Maharashtra","Solapur","nhp",80),
        ("Government Hospital Kolhapur - NH-48","hospital",2,"0231-2659248",None,"Nagala Park, Kolhapur - NH-48",16.7050,74.2433,"Maharashtra","Kolhapur","nhp",80),
        ("Mumbai Police Control Room","police",2,"022-22694488",None,"Crawford Market, Mumbai",18.9462,72.8347,"Maharashtra","Mumbai","state_police_website",86),
        ("Maharashtra Highway Police","police",2,"1033","022-22694488","Maharashtra highway patrol statewide",19.0760,72.8777,"Maharashtra","Mumbai","state_police_website",84),
        ("Maharashtra Ambulance 108","ambulance",1,"108",None,"Maharashtra statewide",None,None,"Maharashtra",None,"government_mandated",100),
        ("AIIMS Delhi","hospital",2,"011-26588500",None,"Ansari Nagar, New Delhi",28.5675,77.2100,"Delhi","New Delhi","nhp",92),
        ("Safdarjung Hospital Delhi","hospital",2,"011-26730000",None,"Ansari Nagar West, New Delhi",28.5680,77.2031,"Delhi","New Delhi","nhp",90),
        ("RML Hospital Delhi","hospital",2,"011-23404263",None,"Baba Kharak Singh Marg, Delhi",28.6327,77.2003,"Delhi","New Delhi","nhp",88),
        ("GTB Hospital Delhi - NH-24","hospital",2,"011-22592671",None,"Dilshad Garden, Delhi - NH-24",28.6725,77.3103,"Delhi","New Delhi","nhp",86),
        ("Delhi Police Control Room","police",2,"011-23490606",None,"ITO, New Delhi",28.6296,77.2463,"Delhi","New Delhi","state_police_website",87),
        ("Govt General Hospital Hyderabad","hospital",2,"040-24600124",None,"Afzalgunj, Hyderabad",17.3752,78.4839,"Telangana","Hyderabad","nhp",85),
        ("Osmania General Hospital Hyderabad","hospital",2,"040-24565182",None,"Musheerabad, Hyderabad",17.3841,78.5067,"Telangana","Hyderabad","nhp",83),
        ("Government Hospital Nizamabad - NH-44","hospital",2,"08462-225656",None,"Nizamabad - NH-44 corridor",18.6725,78.0940,"Telangana","Nizamabad","nhp",80),
        ("Government Hospital Warangal","hospital",2,"0870-2578900",None,"MGM Hospital Rd, Warangal",17.9689,79.5941,"Telangana","Warangal","nhp",81),
        ("Hyderabad Police Control Room","police",2,"040-27852222",None,"Basheerbagh, Hyderabad",17.3957,78.4736,"Telangana","Hyderabad","state_police_website",85),
        ("GGH Visakhapatnam - NH-16","hospital",2,"0891-2564891",None,"Maharani Peta, Vizag - NH-16",17.7231,83.3012,"Andhra Pradesh","Visakhapatnam","nhp",85),
        ("GGH Vijayawada - NH-16","hospital",2,"0866-2574991",None,"Governorpet, Vijayawada - NH-16",16.5193,80.6305,"Andhra Pradesh","Vijayawada","nhp",84),
        ("Government Hospital Kurnool - NH-44","hospital",2,"08518-222218",None,"Budhavarpet, Kurnool - NH-44",15.8281,78.0373,"Andhra Pradesh","Kurnool","nhp",81),
        ("Government Hospital Nellore - NH-16","hospital",2,"0861-2322290",None,"GH Road, Nellore - NH-16",14.4426,79.9865,"Andhra Pradesh","Nellore","nhp",80),
        ("GGH Rajahmundry - NH-16","hospital",2,"0883-2475566",None,"Hospital Road, Rajahmundry - NH-16",17.0005,81.8040,"Andhra Pradesh","Rajahmundry","nhp",81),
        ("Civil Hospital Ahmedabad","hospital",2,"079-22681000",None,"Asarwa, Ahmedabad",23.0497,72.6130,"Gujarat","Ahmedabad","nhp",85),
        ("Surat Civil Hospital - NH-48","hospital",2,"0261-2244000",None,"Majura Gate, Surat - NH-48",21.1959,72.8311,"Gujarat","Surat","nhp",83),
        ("SSG Hospital Vadodara - NH-48","hospital",2,"0265-2431136",None,"Jail Road, Vadodara - NH-48",22.3217,73.1851,"Gujarat","Vadodara","nhp",84),
        ("General Hospital Rajkot - NH-27","hospital",2,"0281-2440797",None,"Rajkot - NH-27",22.3039,70.8022,"Gujarat","Rajkot","nhp",81),
        ("Gujarat Highway Patrol","police",2,"1033","079-23250999","Gujarat highway patrol statewide",23.0225,72.5714,"Gujarat","Ahmedabad","state_police_website",84),
        ("SMS Hospital Jaipur - NH-48","hospital",2,"0141-2518291",None,"JLN Marg, Jaipur - NH-48",26.9004,75.7882,"Rajasthan","Jaipur","nhp",87),
        ("JLN Hospital Ajmer - NH-48","hospital",2,"0145-2627438",None,"Madar Gate, Ajmer - NH-48",26.4499,74.6399,"Rajasthan","Ajmer","nhp",82),
        ("RNT Medical College Udaipur","hospital",2,"0294-2411560",None,"Chetak Circle, Udaipur",24.5854,73.6851,"Rajasthan","Udaipur","nhp",83),
        ("SN Medical College Jodhpur","hospital",2,"0291-2434374",None,"Residency Road, Jodhpur",26.2389,73.0243,"Rajasthan","Jodhpur","nhp",83),
        ("Rajasthan Highway Police","police",2,"1033","0141-2744000","Rajasthan highway patrol statewide",26.9124,75.7873,"Rajasthan","Jaipur","state_police_website",83),
        ("Hamidia Hospital Bhopal - NH-46","hospital",2,"0755-2540211",None,"Royal Market, Bhopal - NH-46",23.2599,77.4126,"Madhya Pradesh","Bhopal","nhp",85),
        ("MY Hospital Indore - NH-52","hospital",2,"0731-2527291",None,"Mochipura, Indore - NH-52",22.7196,75.8577,"Madhya Pradesh","Indore","nhp",85),
        ("NSCB Medical College Jabalpur - NH-44","hospital",2,"0761-2677400",None,"Nagpur Road, Jabalpur - NH-44",23.1688,79.9476,"Madhya Pradesh","Jabalpur","nhp",83),
        ("Gajra Raja Medical College Gwalior - NH-44","hospital",2,"0751-2323204",None,"Lashkar, Gwalior - NH-44",26.2183,78.1828,"Madhya Pradesh","Gwalior","nhp",82),
        ("SN Medical College Agra - NH-44/NH-19","hospital",2,"0562-2360101",None,"Mahatma Gandhi Road, Agra - NH-19",27.1767,78.0081,"Uttar Pradesh","Agra","nhp",85),
        ("KGMU Lucknow - NH-27","hospital",2,"0522-2258880",None,"Shah Mina Road, Lucknow - NH-27",26.8582,80.9346,"Uttar Pradesh","Lucknow","nhp",88),
        ("MLN Medical College Allahabad - NH-19","hospital",2,"0532-2256812",None,"Darbhanga Castle, Allahabad - NH-19",25.4358,81.8463,"Uttar Pradesh","Prayagraj","nhp",83),
        ("BHU IMS Hospital Varanasi - NH-19","hospital",2,"0542-2309488",None,"Lanka, Varanasi - NH-19",25.2677,82.9913,"Uttar Pradesh","Varanasi","nhp",86),
        ("Government Hospital Mathura - NH-19","hospital",2,"0565-2402600",None,"Civil Lines, Mathura - NH-19",27.4924,77.6737,"Uttar Pradesh","Mathura","nhp",80),
        ("District Hospital Kanpur - NH-19","hospital",2,"0512-2553401",None,"GT Road, Kanpur - NH-19",26.4499,80.3319,"Uttar Pradesh","Kanpur","nhp",81),
        ("UP Ambulance 108","ambulance",1,"108",None,"Uttar Pradesh statewide",None,None,"Uttar Pradesh",None,"government_mandated",100),
        ("PGIMER Chandigarh - NH-44","hospital",2,"0172-2755555",None,"Sector 12, Chandigarh - NH-44",30.7652,76.7761,"Chandigarh","Chandigarh","nhp",90),
        ("PGIMS Rohtak - NH-44","hospital",2,"01262-213300",None,"Medical Road, Rohtak - NH-44",28.8955,76.5899,"Haryana","Rohtak","nhp",84),
        ("Civil Hospital Ambala - NH-44","hospital",2,"0171-2535011",None,"Mall Road, Ambala - NH-44",30.3782,76.7767,"Haryana","Ambala","nhp",82),
        ("Civil Hospital Karnal - NH-44","hospital",2,"0184-2268003",None,"GT Road, Karnal - NH-44",29.6857,76.9905,"Haryana","Karnal","nhp",81),
        ("Govt Medical College Amritsar - NH-44","hospital",2,"0183-2501386",None,"Majitha Verka Bypass, Amritsar - NH-44",31.6340,74.8723,"Punjab","Amritsar","nhp",84),
        ("Govt Medical College Ludhiana - NH-44","hospital",2,"0161-2302233",None,"Ludhiana - NH-44",30.9010,75.8573,"Punjab","Ludhiana","nhp",83),
        ("Haryana Highway Patrol","police",2,"1033","0172-2561200","Haryana highway patrol statewide",28.6692,76.9228,"Haryana","Chandigarh","state_police_website",83),
        ("Medical College Hospital Kolkata","hospital",2,"033-22124000",None,"College Street, Kolkata",22.5785,88.3647,"West Bengal","Kolkata","nhp",85),
        ("SSKM Hospital Kolkata","hospital",2,"033-22041441",None,"AJC Bose Road, Kolkata",22.5450,88.3426,"West Bengal","Kolkata","nhp",86),
        ("Durgapur Steel Plant Hospital - NH-19","hospital",2,"0343-2570900",None,"Durgapur - NH-19",23.5204,87.3119,"West Bengal","Durgapur","nhp",80),
        ("West Bengal Ambulance 108","ambulance",1,"108",None,"West Bengal statewide",None,None,"West Bengal",None,"government_mandated",100),
        ("SCB Medical College Cuttack - NH-16","hospital",2,"0671-2414003",None,"Mangalabag, Cuttack - NH-16",20.4686,85.8792,"Odisha","Cuttack","nhp",85),
        ("Capital Hospital Bhubaneswar - NH-16","hospital",2,"0674-2390223",None,"Unit 6, Bhubaneswar - NH-16",20.2961,85.8245,"Odisha","Bhubaneswar","nhp",84),
        ("VIMSAR Burla - NH-53","hospital",2,"0663-2430740",None,"Burla, Sambalpur - NH-53",21.4956,83.8745,"Odisha","Sambalpur","nhp",83),
        ("PMCH Patna - NH-19","hospital",2,"0612-2300610",None,"PMCH Road, Patna - NH-19",25.6103,85.1391,"Bihar","Patna","nhp",85),
        ("NMCH Patna","hospital",2,"0612-2631077",None,"Agamkuan, Patna",25.5941,85.1576,"Bihar","Patna","nhp",83),
        ("JLNMCH Bhagalpur - NH-80","hospital",2,"0641-2400467",None,"Mayaganj, Bhagalpur - NH-80",25.2548,87.0214,"Bihar","Bhagalpur","nhp",81),
        ("RIMS Ranchi - NH-23","hospital",2,"0651-2542441",None,"Bariatu, Ranchi - NH-23",23.3441,85.3096,"Jharkhand","Ranchi","nhp",83),
        ("MGM Medical College Jamshedpur - NH-33","hospital",2,"0657-2426999",None,"Dimna Road, Jamshedpur - NH-33",22.8046,86.2029,"Jharkhand","Jamshedpur","nhp",82),
        ("MCH Thiruvananthapuram","hospital",2,"0471-2528386",None,"Ulloor, Thiruvananthapuram",8.5241,76.9366,"Kerala","Thiruvananthapuram","nhp",84),
        ("Govt Medical College Kozhikode - NH-66","hospital",2,"0495-2350216",None,"Medical College Rd, Kozhikode - NH-66",11.2588,75.7804,"Kerala","Kozhikode","nhp",83),
        ("Govt Medical College Thrissur","hospital",2,"0487-2361601",None,"Thrissur - NH-544",10.5276,76.2144,"Kerala","Thrissur","nhp",82),
        ("Govt Medical College Ernakulam - NH-66","hospital",2,"0484-2361601",None,"Kalamassery, Ernakulam - NH-66",10.0525,76.3506,"Kerala","Ernakulam","nhp",83),
        ("Govt Hospital Palakkad - NH-544","hospital",2,"0491-2505261",None,"Palakkad - NH-544",10.7867,76.6548,"Kerala","Palakkad","nhp",80),
        ("Kerala DISHA Helpline 1056","ambulance",1,"1056",None,"Kerala statewide emergency helpline",None,None,"Kerala",None,"government_mandated",100),
        ("Goa Medical College Panaji - NH-66","hospital",2,"0832-2458740",None,"Bambolim, Panaji - NH-66",15.4909,73.8278,"Goa","Panaji","nhp",84),
        ("AIIMS Raipur - NH-53","hospital",2,"0771-2573601",None,"GE Road, Raipur - NH-53",21.2514,81.6296,"Chhattisgarh","Raipur","nhp",87),
        ("DR BR Ambedkar Hospital Raipur","hospital",2,"0771-4010109",None,"Jail Road, Raipur",21.2346,81.6302,"Chhattisgarh","Raipur","nhp",84),
        ("SMHS Hospital Srinagar - NH-44","hospital",2,"0194-2452079",None,"Karan Nagar, Srinagar - NH-44",34.0837,74.7973,"Jammu & Kashmir","Srinagar","nhp",82),
        ("Govt Medical College Jammu - NH-44","hospital",2,"0191-2578008",None,"Canal Road, Jammu - NH-44",32.7266,74.8570,"Jammu & Kashmir","Jammu","nhp",82),
        ("NHAI Helpline National","highway_helpline",1,"1033",None,"National Highways all India",None,None,None,None,"government_mandated",100),
        ("NHAI NH-44 Project Office Chennai","highway_helpline",2,"1033","044-28480801","NH-44 southern end Chennai",13.0827,80.2707,"Tamil Nadu","Chennai","nhai",90),
        ("NHAI NH-44 Project Office Nagpur","highway_helpline",2,"1033","0712-2221680","NH-44 central Nagpur",21.1458,79.0882,"Maharashtra","Nagpur","nhai",88),
        ("NHAI NH-44 Project Office Delhi","highway_helpline",2,"1033","011-25074100","NH-44 northern Delhi",28.6139,77.2090,"Delhi","New Delhi","nhai",90),
        ("NHAI NH-48 Project Office Bangalore","highway_helpline",2,"1033","080-25503060","NH-48 Bangalore",12.9141,77.6101,"Karnataka","Bengaluru","nhai",90),
        ("NHAI NH-48 Project Office Gurgaon","highway_helpline",2,"1033","0124-2573636","NH-48 Delhi-Jaipur Gurgaon",28.4595,77.0266,"Haryana","Gurgaon","nhai",90),
        ("NHAI NH-16 Project Office Vizag","highway_helpline",2,"1033","0891-2558577","NH-16 eastern Visakhapatnam",17.7231,83.3012,"Andhra Pradesh","Visakhapatnam","nhai",88),
        ("NHAI NH-19 Project Office Agra","highway_helpline",2,"1033","0562-2526100","NH-19 old NH-2 Agra",27.1767,78.0081,"Uttar Pradesh","Agra","nhai",88),
        ("NHAI NH-66 Project Office Mumbai","highway_helpline",2,"1033","022-25003040","NH-66 west coast Mumbai",19.0760,72.8777,"Maharashtra","Mumbai","nhai",88),
    ]

    cur = conn.cursor()
    for (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf) in contacts:
        cur.execute("""
            INSERT OR IGNORE INTO contacts
            (name, category, tier, phone, phone_alt, address, lat, lon,
             state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf))

    conn.commit()
    print("[DB] Seeded " + str(len(contacts)) + " Tier 2 verified contacts.")


def seed_roadside_services(conn):
    services = [
        ("NHAI Crane & Towing NH-44 Mathura","towing",2,"1033","0565-2431100","Mathura Toll Plaza, NH-44 km 145",27.4924,77.6737,"Uttar Pradesh","Mathura","nhai",82),
        ("Singh Tyre Service NH-44 Agra","puncture",2,"9634112233",None,"Near Runkata Toll, NH-44 km 178",27.2046,78.0148,"Uttar Pradesh","Agra","nhai",75),
        ("NHAI Crane & Towing NH-44 Jhansi","towing",2,"1033","0517-2443990","Jhansi Bypass, NH-44 km 378",25.4484,78.5685,"Uttar Pradesh","Jhansi","nhai",82),
        ("Ramkumar Tyre Repair NH-44 Nagpur","puncture",2,"9823441100",None,"Butibori MIDC Toll, NH-44 km 1063",21.0000,79.1168,"Maharashtra","Nagpur","nhai",75),
        ("NHAI Crane & Towing NH-44 Nagpur","towing",2,"1033","0712-2533466","NHAI Nagpur Regional Office, NH-44",21.1458,79.0882,"Maharashtra","Nagpur","nhai",85),
        ("Murugan Tyre Service NH-44 Krishnagiri","puncture",2,"9787001122",None,"Krishnagiri Toll Plaza, NH-44 km 2127",12.5186,78.2137,"Tamil Nadu","Krishnagiri","nhai",75),
        ("NHAI Crane & Towing NH-44 Hyderabad","towing",2,"1033","040-23324666","Outer Ring Road junction NH-44",17.4065,78.4772,"Telangana","Hyderabad","nhai",85),
        ("NHAI Crane & Towing NH-48 Manesar","towing",2,"1033","0124-2340200","Manesar Toll NH-48 km 45",28.3674,76.9162,"Haryana","Gurugram","nhai",85),
        ("Sharma Tyre Repair NH-48 Jaipur","puncture",2,"9414551122",None,"Jaipur-Ajmer Expressway, NH-48 km 268",26.9124,75.7873,"Rajasthan","Jaipur","nhai",74),
        ("NHAI Crane & Towing NH-48 Pune","towing",2,"1033","020-25705000","Pune Toll Plaza Katraj, NH-48 km 1372",18.4529,73.8588,"Maharashtra","Pune","nhai",85),
        ("Patil Tyre Service NH-48 Pune-Satara","puncture",2,"9881334455",None,"Khopoli ghat approach NH-48 km 1330",18.7667,73.3416,"Maharashtra","Raigad","nhai",73),
        ("NHAI Crane & Towing NH-48 Bengaluru","towing",2,"1033","080-22208090","Tumkur Road NH-48 Bengaluru approach",13.0827,77.5946,"Karnataka","Bengaluru","nhai",85),
        ("Gowda Tyre Service NH-48 Tumkur","puncture",2,"9980221133",None,"Tumkur Bypass NH-48 km 1491",13.3409,77.1010,"Karnataka","Tumkur","nhai",74),
        ("NHAI Crane & Towing NH-19 Kanpur","towing",2,"1033","0512-2531099","Kanpur Toll Plaza NH-19 km 445",26.4499,80.3319,"Uttar Pradesh","Kanpur","nhai",83),
        ("Tripathi Tyre Shop NH-19 Varanasi","puncture",2,"9415771234",None,"Varanasi Bypass NH-19 km 668",25.3176,82.9739,"Uttar Pradesh","Varanasi","nhai",74),
        ("NHAI Crane & Towing NH-19 Dhanbad","towing",2,"1033","0326-2308100","Dhanbad Industrial Belt NH-19 km 1134",23.7957,86.4304,"Jharkhand","Dhanbad","nhai",82),
        ("NHAI Crane & Towing NH-16 Vijayawada","towing",2,"1033","0866-2577900","Vijayawada Toll NH-16 km 1168",16.5062,80.6480,"Andhra Pradesh","Vijayawada","nhai",84),
        ("Reddy Tyre Service NH-16 Nellore","puncture",2,"9440112233",None,"Nellore Bypass NH-16 km 1381",14.4426,79.9865,"Andhra Pradesh","Nellore","nhai",73),
        ("NHAI Crane & Towing NH-66 Ratnagiri","towing",2,"1033","02352-222444","Ratnagiri Ghat NH-66 km 488",16.9902,73.3120,"Maharashtra","Ratnagiri","nhai",83),
        ("Sawant Tyre Repair NH-66 Goa border","puncture",2,"9823001122",None,"Patradevi Goa-Maharashtra border NH-66",15.7139,73.9597,"Goa","North Goa","nhai",73),
        ("NHAI Crane & Towing NH-66 Kozhikode","towing",2,"1033","0495-2720100","Kozhikode Bypass NH-66 km 1297",11.2588,75.7804,"Kerala","Kozhikode","nhai",83),
        ("NHAI Crane & Towing NH-52 Guwahati","towing",2,"1033","0361-2736100","Guwahati Bypass NH-37/NH-52",26.1445,91.7362,"Assam","Guwahati","nhai",81),
        ("Bora Tyre Service NH-37 Kaziranga","puncture",2,"9678001234",None,"Kohora junction NH-37 near Kaziranga",26.5775,93.1700,"Assam","Golaghat","nhai",72),
        ("NHAI 24x7 Towing Dispatch Helpline","towing",1,"1033","1800111363","NHAI HQ New Delhi - dispatches nearest crane anywhere on NH network",28.6139,77.2090,None,"New Delhi","nhai",98),
        ("National Highway Towing 1073","towing",1,"1073",None,"MoRTH Road Accident Relief - coordinates towing + hospital",28.6139,77.2090,None,"New Delhi","government_mandated",97),
    ]

    cur = conn.cursor()
    for (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf) in services:
        cur.execute("""
            INSERT OR IGNORE INTO contacts
            (name, category, tier, phone, phone_alt, address, lat, lon,
             state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf))

    conn.commit()
    print("[DB] Seeded " + str(len(services)) + " roadside services (towing + puncture).")


def seed_trauma_centres(conn):
    trauma = [
        ("AIIMS Trauma Centre New Delhi","trauma",1,"011-26593308","011-26589900","Ansari Nagar, New Delhi - NH-44/48 junction",28.5671,77.2100,"Delhi","New Delhi","aiims",97),
        ("Safdarjung Hospital Trauma Delhi","trauma",2,"011-24673501","011-24675555","Ansari Nagar West, New Delhi - NH-44 km 0",28.5685,77.2060,"Delhi","New Delhi","nhp",93),
        ("PGI Rohtak Trauma Centre - NH-44","trauma",2,"01262-213434","01262-211300","PGIMS Campus, Rohtak - NH-44 km 72",28.8955,76.6066,"Haryana","Rohtak","nhp",88),
        ("SNMC Agra Trauma Centre - NH-44","trauma",2,"0562-2600155","0562-2526100","Fatehabad Road, Agra - NH-44 km 205",27.1767,78.0081,"Uttar Pradesh","Agra","nhp",87),
        ("KGMC Lucknow Trauma Centre - NH-44","trauma",2,"0522-2257540","0522-2257450","Shah Mina Road, Lucknow - NH-44 km 490",26.8578,80.9166,"Uttar Pradesh","Lucknow","nhp",90),
        ("AIIMS Nagpur Trauma - NH-44","trauma",2,"0712-2700005","0712-2533466","MIHAN, Nagpur - NH-44 km 1063",21.0936,79.0476,"Maharashtra","Nagpur","aiims",90),
        ("NIMS Hyderabad Trauma - NH-44","trauma",2,"040-23489000","040-23324666","Punjagutta, Hyderabad - NH-44 km 1511",17.4315,78.4483,"Telangana","Hyderabad","nhp",88),
        ("SMS Hospital Jaipur Trauma - NH-48","trauma",2,"0141-2518888","0141-2560291","Tonk Road, Jaipur - NH-48 km 267",26.8927,75.8036,"Rajasthan","Jaipur","nhp",90),
        ("NIMHANS Bengaluru Neurotrauma - NH-44/48","trauma",2,"080-46110007","080-26995001","Hosur Road, Bengaluru - NH-44/48 junction",12.9401,77.5959,"Karnataka","Bengaluru","nhp",92),
        ("BHU Trauma Centre Varanasi - NH-19","trauma",2,"0542-2367568","0542-2508100","Lanka, Varanasi - NH-19 km 668",25.2677,82.9913,"Uttar Pradesh","Varanasi","nhp",88),
        ("SSKM Hospital Kolkata Trauma - NH-19/16","trauma",2,"033-22041058","033-22043143","AJC Bose Road, Kolkata - NH-16 start",22.5420,88.3503,"West Bengal","Kolkata","nhp",90),
        ("AIIMS Bhubaneswar Trauma - NH-16","trauma",2,"0674-2476789","0674-2476700","Sijua, Bhubaneswar - NH-16 km 512",20.1534,85.6745,"Odisha","Bhubaneswar","aiims",91),
        ("KEM Hospital Mumbai Trauma - NH-66","trauma",2,"022-24107000","022-24138000","Parel, Mumbai - NH-66 km 0",19.0035,72.8407,"Maharashtra","Mumbai","nhp",92),
        ("Government Medical College Kozhikode - NH-66","trauma",2,"0495-2350216","0495-2720100","Kozhikode Medical College, NH-66 km 1297",11.2610,75.7978,"Kerala","Kozhikode","nhp",88),
        ("PGIMER Chandigarh Trauma - NH-44","trauma",1,"0172-2756565","0172-2755555","Sector 12, Chandigarh - NH-44 km 250 from Delhi",30.7650,76.7780,"Punjab","Chandigarh","aiims",95),
    ]

    cur = conn.cursor()
    for (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf) in trauma:
        cur.execute("""
            INSERT OR IGNORE INTO contacts
            (name, category, tier, phone, phone_alt, address, lat, lon,
             state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf))

    conn.commit()
    print("[DB] Seeded " + str(len(trauma)) + " MoRTH trauma centres.")


def seed_blood_banks(conn):
    blood_banks = [
        ("AIIMS Blood Bank New Delhi","blood_bank",1,"011-26593308","011-26589900","AIIMS Campus, Ansari Nagar, New Delhi - NH-44/48",28.5671,77.2100,"Delhi","New Delhi","nbtc",97),
        ("Safdarjung Hospital Blood Bank Delhi","blood_bank",2,"011-24673488","011-24675555","Ansari Nagar West, New Delhi - NH-44",28.5685,77.2060,"Delhi","New Delhi","nbtc",93),
        ("PGIMER Blood Bank Chandigarh","blood_bank",1,"0172-2756767","0172-2755555","Sector 12, Chandigarh - NH-44 km 250",30.7650,76.7780,"Punjab","Chandigarh","nbtc",96),
        ("SMS Hospital Blood Bank Jaipur","blood_bank",2,"0141-2518055","0141-2560291","Tonk Road, Jaipur - NH-48 km 267",26.8927,75.8036,"Rajasthan","Jaipur","nbtc",91),
        ("KGMC Blood Bank Lucknow","blood_bank",2,"0522-2257450","0522-2257540","Shah Mina Road, Lucknow - NH-44 km 490",26.8578,80.9166,"Uttar Pradesh","Lucknow","nbtc",91),
        ("Government Medical College Blood Bank Nagpur","blood_bank",2,"0712-2700088","0712-2533466","Medical Square, Nagpur - NH-44 km 1063",21.1370,79.0888,"Maharashtra","Nagpur","nbtc",89),
        ("Osmania Hospital Blood Bank Hyderabad","blood_bank",2,"040-24600132","040-23324666","Afzalgunj, Hyderabad - NH-44 km 1511",17.3778,78.4733,"Telangana","Hyderabad","nbtc",90),
        ("Govt. Stanley Hospital Blood Bank Chennai","blood_bank",2,"044-25281201","044-25281200","Old Jail Road, Chennai - NH-44 terminus",13.1102,80.2887,"Tamil Nadu","Chennai","nbtc",90),
        ("Victoria Hospital Blood Bank Bengaluru","blood_bank",2,"080-26701159","080-26701150","Fort Road, Bengaluru - NH-44/48 junction",12.9636,77.5854,"Karnataka","Bengaluru","nbtc",91),
        ("KEM Hospital Blood Bank Mumbai","blood_bank",2,"022-24138053","022-24107000","Parel, Mumbai - NH-66 start",19.0035,72.8407,"Maharashtra","Mumbai","nbtc",92),
        ("SSKM Blood Bank Kolkata","blood_bank",2,"033-22041056","033-22043143","AJC Bose Road, Kolkata - NH-16/19",22.5420,88.3503,"West Bengal","Kolkata","nbtc",91),
        ("AIIMS Bhubaneswar Blood Bank - NH-16","blood_bank",2,"0674-2476780","0674-2476700","Sijua, Bhubaneswar - NH-16 km 512",20.1534,85.6745,"Odisha","Bhubaneswar","nbtc",91),
    ]

    cur = conn.cursor()
    for (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf) in blood_banks:
        cur.execute("""
            INSERT OR IGNORE INTO contacts
            (name, category, tier, phone, phone_alt, address, lat, lon,
             state, district, country_code, source, confidence, is_active)
            VALUES (?,?,?,?,?,?,?,?,?,?,'IN',?,?,1)
        """, (name, cat, tier, phone, phone_alt, addr, lat, lon, state, dist, source, conf))

    conn.commit()
    print("[DB] Seeded " + str(len(blood_banks)) + " blood banks.")


if __name__ == "__main__":
    from database.seed_districts import seed_districts
    from database.seed_specialty_hospitals import seed_specialty_hospitals
    conn = init_db()
    seed_national_numbers(conn)
    seed_tier2_contacts(conn)
    seed_roadside_services(conn)
    seed_trauma_centres(conn)
    seed_blood_banks(conn)
    seed_districts(conn)
    seed_specialty_hospitals(conn)
    conn.close()
    # Run phonenumbers verification on all seeded contacts
    try:
        from verify_numbers import verify_all_contacts
        verify_all_contacts(DB_PATH)
    except Exception as e:
        print("[verify] Skipped: " + str(e))
    print("\n[DB] Database ready: " + DB_PATH)
    print("[DB] Run: streamlit run app.py")
