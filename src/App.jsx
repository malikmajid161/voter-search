import React, { useState, useEffect, useMemo } from 'react';
import { 
  Search, User, FileText, Home, Filter, ShieldCheck, CheckCircle2, 
  Users, ArrowLeft, Bookmark, BookmarkCheck, BarChart3, Sun, Moon,
  Printer, X, ChevronRight, ChevronDown, ChevronUp, MapPin, UserCheck, RefreshCw, Copy, Check, Plus,
  Download, ZoomIn, ZoomOut, Maximize2, Sparkles, Share2, Landmark, Building2, MessageSquare, PhoneCall
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import voterDataRaw from './voter_data_final.json';
import familyDataRaw from './family_data.json';

// Dynamic Polling Location Mapping based on Block Code & Gender
const getPollingStation = (blockCode, gender) => {
  const isFemale = (gender || '').toLowerCase() === 'female';
  const block = String(blockCode || '').replace(/\D/g, '');

  if (['266010901', '266010902', '266010903'].includes(block)) {
    return isFemale 
      ? 'Govt Girls High School Mardwal (گورنمنٹ گرلز ہائی سکول مردوال - زنانہ)' 
      : 'Govt High School Mardwal (گورنمنٹ ہائی سکول مردوال - مردانہ)';
  } else if (['266010904', '266010905', '266010906'].includes(block)) {
    return isFemale 
      ? 'Govt Primary School Mardwal (گورنمنٹ پرائمری سکول مردوال - زنانہ)' 
      : 'Govt High School Mardwal (گورنمنٹ ہائی سکول مردوال - مردانہ)';
  } else {
    return isFemale 
      ? 'Govt Girls High School Mardwal (گورنمنٹ گرلز ہائی سکول مردوال - زنانہ)' 
      : 'Govt Primary School Mardwal (گورنمنٹ پرائمری سکول مردوال - مردانہ)';
  }
};

// Automatic Android / iOS native SMS trigger for ECP 8300 helpline
const sendSmsTo8300 = (cnic = '') => {
  const cleanCnic = String(cnic || '').replace(/\D/g, '');
  window.location.href = `sms:8300?body=${cleanCnic}`;
};

// Unique Field Record Lookup Utility: Never fetch by array index (e.g. voterData[silsilaNo])
export const findVoterRecord = (voterList, silsilaNo, blockCode = null, cnic = null) => {
  if (!voterList || !Array.isArray(voterList)) return null;

  if (cnic) {
    const cleanCnic = String(cnic).replace(/\D/g, '');
    const matched = voterList.find(v => (v.CNIC || '').replace(/\D/g, '') === cleanCnic);
    if (matched) return matched;
  }

  if (silsilaNo !== undefined && silsilaNo !== null) {
    const targetSilsila = String(silsilaNo).trim();
    if (blockCode) {
      const targetBlock = String(blockCode).replace(/\D/g, '').trim();
      const matched = voterList.find(v => 
        String(v.SilsilaNo || '').trim() === targetSilsila && 
        String(v.BlockCode || '').replace(/\D/g, '').trim() === targetBlock
      );
      if (matched) return matched;
    }
    const matchedBySilsila = voterList.find(v => String(v.SilsilaNo || '').trim() === targetSilsila);
    if (matchedBySilsila) return matchedBySilsila;
  }

  return null;
};

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [splashProgress, setSplashProgress] = useState(0);
  const [voterData, setVoterData] = useState([]);
  const [familyData, setFamilyData] = useState({});
  const [loading, setLoading] = useState(true);
  
  // Navigation & View States
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'families', 'stats', 'bookmarks'
  const [selectedFamilyId, setSelectedFamilyId] = useState(null);
  const [printVoter, setPrintVoter] = useState(null);
  const [showFilterDrawer, setShowFilterDrawer] = useState(false);
  const [copiedCNIC, setCopiedCNIC] = useState(null);
  
  // Expanded Frames State for Voter Cards (Map of cnic -> boolean)
  const [expandedFrames, setExpandedFrames] = useState({});
  
  // Zoom & Modal Image States
  const [zoomModalImage, setZoomModalImage] = useState(null);
  const [modalZoomScale, setModalZoomScale] = useState(1);

  // Search & Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [familySearchQuery, setFamilySearchQuery] = useState('');
  const [genderFilter, setGenderFilter] = useState('all');
  const [blockFilter, setBlockFilter] = useState('all');
  const [ageFilter, setAgeFilter] = useState('all');

  // Dynamic Pagination Limit State
  const [displayLimit, setDisplayLimit] = useState(50);

  // App Theme & Bookmarks
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('voter_app_theme') === 'dark';
  });
  const [bookmarks, setBookmarks] = useState(() => {
    const saved = localStorage.getItem('voter_app_bookmarks');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('voter_app_theme', darkMode ? 'dark' : 'light');
    if (darkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('voter_app_bookmarks', JSON.stringify(bookmarks));
  }, [bookmarks]);

  // Splash progress animation
  useEffect(() => {
    const interval = setInterval(() => {
      setSplashProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setShowSplash(false), 200);
          return 100;
        }
        return prev + 10;
      });
    }, 80);

    try {
      const indexedVoters = voterDataRaw.map(v => {
        const cnicClean = (v.CNIC || '').replace(/-/g, '');
        const nameLower = (v.NameUrdu || '').toLowerCase();
        const fatherLower = (v.FatherNameUrdu || '').toLowerCase();
        const gharana = String(v.GharanaNo || '');
        const silsila = String(v.SilsilaNo || '');
        const block = String(v.BlockCode || '').replace(/\D/g, '');

        return {
          ...v,
          BlockCode: block || v.BlockCode,
          _searchIndex: `${cnicClean} ${v.CNIC} ${nameLower} ${fatherLower} ${gharana} ${silsila} ${block}`
        };
      });

      setVoterData(indexedVoters);
      setFamilyData(familyDataRaw);
      setLoading(false);
    } catch (err) {
      console.error("Error initializing voter database:", err);
      setLoading(false);
    }

    return () => clearInterval(interval);
  }, []);

  // Reset pagination limit when search query or filters change
  useEffect(() => {
    setDisplayLimit(50);
  }, [searchQuery, genderFilter, blockFilter, ageFilter]);

  // Automatic CNIC Dash Insertion Logic
  const handleSearchInputChange = (e) => {
    const rawVal = e.target.value;
    const digitsOnly = rawVal.replace(/\D/g, '');
    
    if (/^[\d-]+$/.test(rawVal) && digitsOnly.length > 0) {
      let formatted = digitsOnly;
      if (digitsOnly.length > 5 && digitsOnly.length <= 12) {
        formatted = `${digitsOnly.slice(0, 5)}-${digitsOnly.slice(5)}`;
      } else if (digitsOnly.length > 12) {
        formatted = `${digitsOnly.slice(0, 5)}-${digitsOnly.slice(5, 12)}-${digitsOnly.slice(12, 13)}`;
      }
      setSearchQuery(formatted);
    } else {
      setSearchQuery(rawVal);
    }
  };

  const toggleBookmark = (cnic) => {
    setBookmarks(prev => 
      prev.includes(cnic) ? prev.filter(c => c !== cnic) : [...prev, cnic]
    );
  };

  const handleCopyCNIC = (cnic) => {
    navigator.clipboard.writeText(cnic);
    setCopiedCNIC(cnic);
    setTimeout(() => setCopiedCNIC(null), 2000);
  };

  const toggleFrameExpand = (cnic) => {
    setExpandedFrames(prev => ({
      ...prev,
      [cnic]: !prev[cnic]
    }));
  };

  // Image Gallery Download Handler
  const downloadImageToGallery = (imgUrl, fileName) => {
    fetch(imgUrl)
      .then(res => res.blob())
      .then(blob => {
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
      })
      .catch(err => console.error("Error downloading image:", err));
  };

  // Full PDF Document Download
  const downloadFullPdfDocument = () => {
    const link = document.createElement('a');
    link.href = '/Voting_List_Full_2023.pdf';
    link.download = 'Mardwal_Electoral_Voting_List_Full_2023.pdf';
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  // WhatsApp Slip Share Handler
  const shareOnWhatsApp = (voter) => {
    const psName = getPollingStation(voter.BlockCode, voter.Gender);
    const text = `🗳️ *Electoral Voter Verification Slip 2023*\n\n` +
      `👤 *Voter Name:* ${voter.NameUrdu}\n` +
      `👤 *Father/Husband:* ${voter.FatherNameUrdu}\n` +
      `🪪 *CNIC:* ${voter.CNIC}\n` +
      `🔢 *Silsila No:* #${voter.SilsilaNo}\n` +
      `🏠 *Gharana No:* #${voter.GharanaNo}\n` +
      `📦 *Block Code:* ${voter.BlockCode}\n` +
      `🏛️ *Constituency:* NA-88 / PP-84 Khushab\n` +
      `📍 *Polling Station:* ${psName}\n\n` +
      `✅ Verified via Mardwal Voter Pro Portal`;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
  };

  // Get unique clean 9-digit block codes for filtering
  const availableBlockCodes = useMemo(() => {
    const blocks = new Set();
    voterData.forEach(v => {
      const match = String(v.BlockCode || '').match(/\d{9}/);
      if (match) blocks.add(match[0]);
    });
    return Array.from(blocks).sort();
  }, [voterData]);

  // Total matching records before pagination limit
  const totalMatchingRecords = useMemo(() => {
    let result = voterData;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const qClean = q.replace(/-/g, '');
      const silsilaMatch = q.match(/^#?(\d+)$/);

      result = result.filter(v => {
        // Direct field comparison by SilsilaNo or search index string match
        if (silsilaMatch && String(v.SilsilaNo || '').trim() === silsilaMatch[1]) {
          return true;
        }
        return v._searchIndex.includes(q) || v._searchIndex.includes(qClean);
      });
    }

    if (genderFilter !== 'all') {
      result = result.filter(v => (v.Gender || '').toLowerCase() === genderFilter.toLowerCase());
    }

    if (blockFilter !== 'all') {
      result = result.filter(v => v.BlockCode === blockFilter);
    }

    if (ageFilter !== 'all') {
      result = result.filter(v => {
        const age = parseInt(v.Age, 10);
        if (isNaN(age)) return false;
        if (ageFilter === '18-30') return age >= 18 && age <= 30;
        if (ageFilter === '31-50') return age >= 31 && age <= 50;
        if (ageFilter === '50+') return age > 50;
        return true;
      });
    }

    return result;
  }, [searchQuery, genderFilter, blockFilter, ageFilter, voterData]);

  // Check if active search or filter is applied
  const isSearchActive = useMemo(() => {
    return searchQuery.trim().length > 0 || genderFilter !== 'all' || blockFilter !== 'all' || ageFilter !== 'all';
  }, [searchQuery, genderFilter, blockFilter, ageFilter]);

  // Paginated/Sliced Data for rendering performance
  const filteredData = useMemo(() => {
    if (!isSearchActive) return [];
    return totalMatchingRecords.slice(0, displayLimit);
  }, [totalMatchingRecords, displayLimit, isSearchActive]);

  // Filtered Families list for Households Tab
  const filteredFamilies = useMemo(() => {
    const familyList = Object.values(familyData);
    if (!familySearchQuery.trim()) return familyList.slice(0, 60);

    const q = familySearchQuery.toLowerCase().trim();
    const qClean = q.replace(/-/g, '');

    return familyList.filter(fam => {
      const gMatch = fam.gharanaNo.toLowerCase().includes(q);
      const bMatch = fam.blockCode.toLowerCase().includes(q);
      const memberMatch = fam.members.some(m => 
        (m.NameUrdu || '').toLowerCase().includes(q) || 
        (m.FatherNameUrdu || '').toLowerCase().includes(q) ||
        (m.CNIC || '').replace(/-/g, '').includes(qClean)
      );
      return gMatch || bMatch || memberMatch;
    }).slice(0, 80);
  }, [familySearchQuery, familyData]);

  // Saved Bookmarked Voters (lookup by unique CNIC)
  const bookmarkedVoters = useMemo(() => {
    return bookmarks
      .map(cnic => findVoterRecord(voterData, null, null, cnic))
      .filter(Boolean);
  }, [voterData, bookmarks]);

  // Analytics Stats
  const statistics = useMemo(() => {
    const total = voterData.length;
    if (!total) return null;

    let males = 0;
    let females = 0;
    let youth = 0;
    let middle = 0;
    let seniors = 0;

    voterData.forEach(v => {
      if ((v.Gender || '').toLowerCase() === 'male') males++;
      if ((v.Gender || '').toLowerCase() === 'female') females++;

      const age = parseInt(v.Age, 10);
      if (!isNaN(age)) {
        if (age >= 18 && age <= 30) youth++;
        else if (age >= 31 && age <= 50) middle++;
        else if (age > 50) seniors++;
      }
    });

    const totalFamilies = Object.keys(familyData).length;
    const avgFamilySize = (total / (totalFamilies || 1)).toFixed(1);

    return {
      total,
      males,
      females,
      youth,
      middle,
      seniors,
      totalFamilies,
      avgFamilySize,
      malePercent: Math.round((males / total) * 100),
      femalePercent: Math.round((females / total) * 100),
    };
  }, [voterData, familyData]);

  // Splash Screen Renderer
  if (showSplash) {
    return (
      <AnimatePresence>
        <motion.div 
          className="splash-screen"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.4 }}
        >
          <motion.div 
            className="splash-logo"
            initial={{ scale: 0.7, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, type: 'spring' }}
          >
            <ShieldCheck size={72} className="text-emerald-500" />
          </motion.div>

          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="splash-title"
          >
            Mardwal Voter <span>Pro</span>
          </motion.h1>

          <motion.p 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="splash-subtitle"
          >
            NA-88 / PP-84 Khushab Verified Electoral Roll
          </motion.p>

          <div className="splash-progress-wrapper">
            <div className="splash-progress-bar" style={{ width: `${splashProgress}%` }}></div>
          </div>
          <span className="splash-progress-text">{splashProgress}% Loaded</span>
        </motion.div>
      </AnimatePresence>
    );
  }

  // Voter Card Renderer Component
  const renderVoterCard = (voter, idx, isFamilyView = false) => {
    const isBookmarked = bookmarks.includes(voter.CNIC);
    const isCopied = copiedCNIC === voter.CNIC;
    const isFrameOpen = !!expandedFrames[voter.CNIC];
    const pageNum = voter.PageNo || voter.Page || 2;
    const snippetUrl = `/names/${voter.CNIC}.jpg`;
    const pageFrameUrl = `/pages/page_${pageNum}.jpg`;
    const pollingStationName = getPollingStation(voter.BlockCode, voter.Gender);

    return (
      <motion.div 
        className="voter-card" 
        key={voter.CNIC + '_' + idx}
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: Math.min(idx * 0.03, 0.25) }}
      >
        {/* Card Header */}
        <div className="voter-card-top">
          <div className="cnic-wrapper">
            <span className="cnic-text">{voter.CNIC}</span>
            <button 
              className="copy-cnic-btn" 
              onClick={() => handleCopyCNIC(voter.CNIC)}
              title="Copy CNIC"
            >
              {isCopied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} />}
            </button>
            <span className={`gender-tag ${voter.Gender?.toLowerCase()}`}>
              {voter.Gender || 'Male'}
            </span>
          </div>
          
          <div className="card-top-actions">
            <button 
              className={`bookmark-btn ${isBookmarked ? 'active' : ''}`}
              onClick={() => toggleBookmark(voter.CNIC)}
              title={isBookmarked ? "Remove Bookmark" : "Save Voter"}
            >
              {isBookmarked ? <BookmarkCheck size={17} /> : <Bookmark size={17} />}
            </button>
            <button 
              className="print-action-btn"
              onClick={() => setPrintVoter(voter)}
              title="Print Digital Voter Slip"
            >
              <Printer size={17} />
            </button>
          </div>
        </div>

        {/* Polling Location Banner */}
        <div className="card-polling-banner">
          <MapPin size={14} className="text-emerald-600 shrink-0" />
          <span className="polling-banner-text">
            Polling: <strong>{pollingStationName}</strong>
          </span>
        </div>

        {/* Voter Badges Grid */}
        <div className="voter-badges-grid">
          <div className="badge-item">
            <span className="badge-lbl">SILSILA NO</span>
            <span className="badge-val">#{voter.SilsilaNo}</span>
          </div>
          <div className="badge-item">
            <span className="badge-lbl">GHARANA NO</span>
            <span className="badge-val">#{voter.GharanaNo}</span>
          </div>
          <div className="badge-item">
            <span className="badge-lbl">BLOCK CODE</span>
            <span className="badge-val">{voter.BlockCode}</span>
          </div>
          <div className="badge-item">
            <span className="badge-lbl">AGE</span>
            <span className="badge-val">{voter.Age} Yrs</span>
          </div>
        </div>

        {/* Urdu Voter Names Section (RTL Layout) */}
        <div className="name-columns-container">
          <div className="name-column-box name-right">
            <span className="detail-label">نام (Voter Name)</span>
            <span className="detail-value urdu-text">{voter.NameUrdu || 'نام موجود نہیں'}</span>
          </div>

          <div className="name-column-box name-left">
            <span className="detail-label">ولدیت (Father / Husband)</span>
            <span className="detail-value urdu-text">{voter.FatherNameUrdu || 'ولدیت موجود نہیں'}</span>
          </div>
        </div>

        {/* Calligraphy Crop Snippet & Save Snippet Button */}
        <div className="scanned-calligraphy-wrapper">
          <div className="calligraphy-img-box">
            <img 
              src={snippetUrl} 
              alt="Urdu Calligraphy"
              className="scanned-calligraphy-img cursor-pointer"
              loading="lazy"
              onClick={() => {
                setZoomModalImage(snippetUrl);
                setModalZoomScale(1.5);
              }}
              title="Click to Zoom Calligraphy"
              onError={(e) => {
                const wrapper = e.target.closest('.scanned-calligraphy-wrapper');
                if (wrapper) wrapper.style.display = 'none';
              }}
            />
          </div>
          <button 
            className="save-gallery-btn"
            onClick={() => downloadImageToGallery(snippetUrl, `${voter.CNIC}_calligraphy.jpg`)}
            title="Save Calligraphy Snippet to Device Gallery"
          >
            <Download size={13} />
            <span>Save Calligraphy</span>
          </button>
        </div>

        {/* Expandable PDF Page Frame Dropdown Accordion */}
        <div className="frame-accordion-wrapper">
          <button 
            className={`frame-accordion-trigger ${isFrameOpen ? 'open' : ''}`}
            onClick={() => toggleFrameExpand(voter.CNIC)}
          >
            <FileText size={16} className="text-emerald-500" />
            <span>{isFrameOpen ? `Hide PDF Page ${pageNum} Frame` : `View PDF Page ${pageNum} Frame`}</span>
            {isFrameOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          <AnimatePresence>
            {isFrameOpen && (
              <motion.div 
                className="frame-accordion-content"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="frame-viewer-box">
                  <div className="frame-toolbar">
                    <span className="frame-info-txt">PDF Page #{pageNum} (Gharana #{voter.GharanaNo})</span>
                    <div className="frame-actions-group">
                      <button 
                        onClick={() => {
                          setZoomModalImage(pageFrameUrl);
                          setModalZoomScale(1);
                        }}
                        title="Zoom Page Frame Fullscreen"
                      >
                        <Maximize2 size={15} />
                      </button>
                      <button 
                        className="download-frame-btn"
                        onClick={() => downloadImageToGallery(pageFrameUrl, `${voter.CNIC}_Page_${pageNum}.jpg`)}
                        title="Save PDF Page Frame to Device Gallery"
                      >
                        <Download size={14} />
                        <span>Save Page {pageNum}</span>
                      </button>
                    </div>
                  </div>

                  <div 
                    className="frame-img-container cursor-pointer"
                    onClick={() => {
                      setZoomModalImage(pageFrameUrl);
                      setModalZoomScale(1.2);
                    }}
                  >
                    <img 
                      src={pageFrameUrl} 
                      alt={`PDF Page ${pageNum}`} 
                      className="pdf-page-frame-img"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Family Member Trigger Button */}
        {!isFamilyView && voter.FamilyId && familyData[voter.FamilyId] && familyData[voter.FamilyId].members.length > 1 && (
          <button 
            className="family-btn"
            onClick={() => setSelectedFamilyId(voter.FamilyId)}
          >
            <Users size={16} />
            <span>View Gharana Household ({familyData[voter.FamilyId].members.length} Members)</span>
            <ChevronRight size={16} className="ml-auto" />
          </button>
        )}
        {/* Card Primary Actions Bar */}
        <div className="card-primary-actions-bar">
          <button 
            className="whatsapp-share-pill-btn"
            onClick={() => shareOnWhatsApp(voter)}
            title="Share Voter Slip via WhatsApp"
          >
            <Share2 size={16} />
            <span>WhatsApp Slip</span>
          </button>
          <button 
            className="sms-8300-pill-btn"
            onClick={() => sendSmsTo8300(voter.CNIC)}
            title="Send SMS to ECP 8300 Helpline"
          >
            <MessageSquare size={16} />
            <span>ECP 8300 SMS</span>
          </button>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="app-container">
      {/* Mobile Top Header Bar */}
      <header className="mobile-header">
        {selectedFamilyId ? (
          <div className="header-left cursor-pointer" onClick={() => setSelectedFamilyId(null)}>
            <ArrowLeft className="text-emerald-500" size={22} />
            <span className="header-page-title">Gharana Household Details</span>
          </div>
        ) : (
          <div className="header-left">
            <div className="app-icon-bg">
              <ShieldCheck className="text-emerald-500" size={22} />
            </div>
            <div>
              <h2 className="header-app-name">Voter<span>Pro</span></h2>
              <p className="header-sub">Mardwal Registry 2023</p>
            </div>
          </div>
        )}
        
        <div className="header-right">
          {/* Download Full PDF Document Action Button */}
          <button 
            className="header-download-pdf-btn"
            onClick={downloadFullPdfDocument}
            title="Download Full 2023 Electoral PDF (299 Pages)"
          >
            <Download size={15} />
            <span className="hide-mobile">PDF (16MB)</span>
          </button>

          <button 
            className="icon-circle-btn" 
            onClick={() => setDarkMode(!darkMode)}
            title="Toggle Dark/Light Theme"
          >
            {darkMode ? <Sun size={18} className="text-amber-400" /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {/* Main View Area */}
      <main className="main-content">
        {loading ? (
          <div className="loading-state">
            <RefreshCw className="animate-spin text-emerald-500" size={32} />
            <p>Loading database records...</p>
          </div>
        ) : selectedFamilyId ? (
          /* Family Detail Sub-Page View */
          <div className="family-detail-view fade-in">
            <div className="family-summary-banner">
              <div className="family-banner-top">
                <div>
                  <span className="fam-lbl">Household Registry</span>
                  <h3>Gharana No: {familyData[selectedFamilyId]?.gharanaNo}</h3>
                </div>
                <div className="fam-count-badge">
                  <Users size={16} />
                  <span>{familyData[selectedFamilyId]?.members.length} Members</span>
                </div>
              </div>
              <div className="family-meta-row">
                <span><MapPin size={14} /> Block: {familyData[selectedFamilyId]?.blockCode}</span>
                <span><Landmark size={14} /> NA-88 / PP-84 Khushab</span>
              </div>
            </div>

            <div className="section-title-row">
              <h4>Registered Household Members</h4>
            </div>

            <div className="voter-list">
              {familyData[selectedFamilyId]?.members.map((member, idx) => {
                const voter = findVoterRecord(voterData, member.SilsilaNo, member.BlockCode, member.CNIC) || member;
                return renderVoterCard(voter, idx, true);
              })}
            </div>
          </div>
        ) : (
          /* Main Bottom Nav Content Views */
          <>
            {/* TAB 1: HOME SEARCH */}
            {activeTab === 'home' && (
              <div className="search-tab-view fade-in">
                {/* Search Box */}
                <div className="search-box-wrapper">
                  <div className="search-field-container">
                    <Search size={18} className="search-icon" />
                    <input 
                      type="text" 
                      placeholder="Enter CNIC (e.g. 38201...), Name, or Gharana..." 
                      value={searchQuery}
                      onChange={handleSearchInputChange}
                    />
                    {searchQuery && (
                      <button className="clear-search-btn" onClick={() => setSearchQuery('')}>
                        <X size={16} />
                      </button>
                    )}
                  </div>
                  <button 
                    className={`filter-drawer-trigger ${genderFilter !== 'all' || blockFilter !== 'all' || ageFilter !== 'all' ? 'active' : ''}`}
                    onClick={() => setShowFilterDrawer(true)}
                    title="Filters"
                  >
                    <Filter size={18} />
                  </button>
                </div>

                {/* 1-Click Gender Selection Tabs (Male / Female Lists) */}
                <div className="gender-toggle-tabs">
                  <button 
                    className={`gender-tab-btn ${genderFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setGenderFilter('all')}
                  >
                    👥 All Voters
                  </button>
                  <button 
                    className={`gender-tab-btn male-tab ${genderFilter === 'Male' ? 'active' : ''}`}
                    onClick={() => setGenderFilter('Male')}
                  >
                    👨 Male List (مردانہ)
                  </button>
                  <button 
                    className={`gender-tab-btn female-tab ${genderFilter === 'Female' ? 'active' : ''}`}
                    onClick={() => setGenderFilter('Female')}
                  >
                    👩 Female List (زنانہ)
                  </button>
                </div>

                {/* Filter Tags Indicator */}
                {(genderFilter !== 'all' || blockFilter !== 'all' || ageFilter !== 'all') && (
                  <div className="active-filter-pills">
                    {genderFilter !== 'all' && (
                      <span className="filter-pill">
                        Gender: {genderFilter}
                        <X size={12} onClick={() => setGenderFilter('all')} />
                      </span>
                    )}
                    {blockFilter !== 'all' && (
                      <span className="filter-pill">
                        Block: {blockFilter}
                        <X size={12} onClick={() => setBlockFilter('all')} />
                      </span>
                    )}
                    {ageFilter !== 'all' && (
                      <span className="filter-pill">
                        Age: {ageFilter}
                        <X size={12} onClick={() => setAgeFilter('all')} />
                      </span>
                    )}
                    <button className="clear-all-pills" onClick={() => {
                      setGenderFilter('all');
                      setBlockFilter('all');
                      setAgeFilter('all');
                    }}>Reset All</button>
                  </div>
                )}

                {/* STARTER DASHBOARD SCREEN (Rich & Beautiful UI) */}
                {!isSearchActive ? (
                  <div className="dashboard-starter-container fade-in">
                    {/* Hero Card with Key Metrics */}
                    <div className="dashboard-hero-card">
                      <div className="hero-icon-circle">
                        <ShieldCheck size={32} className="text-emerald-500" />
                      </div>
                      <h3>Mardwal Electoral Registry 2023</h3>
                      <p>Official voter verification portal for <strong>NA-88 Khushab-II</strong> and <strong>PP-84 Khushab-IV</strong> (مرکزِ مردوال).</p>
                      
                      <div className="starter-stats-row">
                        <div className="starter-stat-item">
                          <Users size={16} className="text-emerald-500" />
                          <span><strong>7,171</strong> Voters</span>
                        </div>
                        <div className="starter-stat-item">
                          <Home size={16} className="text-emerald-500" />
                          <span><strong>1,300+</strong> Gharanas</span>
                        </div>
                        <div className="starter-stat-item">
                          <FileText size={16} className="text-emerald-500" />
                          <span><strong>299</strong> Pages</span>
                        </div>
                      </div>

                      <button 
                        className="download-full-pdf-hero-btn"
                        onClick={downloadFullPdfDocument}
                      >
                        <Download size={18} />
                        Download Complete 2023 Electoral PDF (299 Pages)
                      </button>
                    </div>

                    {/* Official Polling Station Info & ECP 8300 Banner */}
                    <div className="polling-hero-card">
                      <div className="polling-card-head">
                        <MapPin size={18} className="text-emerald-500 shrink-0" />
                        <div>
                          <h4>ECP Voter Verification Helpline</h4>
                          <p>Send CNIC to <strong>8300</strong> to receive official ECP SMS details on mobile.</p>
                        </div>
                      </div>
                      <div className="polling-card-footer">
                        <button className="sms-trigger-chip" onClick={() => sendSmsTo8300('38201')}>
                          <MessageSquare size={14} /> Click to Send SMS to 8300
                        </button>
                      </div>
                    </div>

                    {/* Block Code Filtering Section */}
                    <div className="starter-blocks-section">
                      <h4>Explore Voters by Block Code:</h4>
                      <div className="quick-block-grid">
                        {availableBlockCodes.map(block => (
                          <button 
                            key={block} 
                            className="block-chip"
                            onClick={() => setBlockFilter(block)}
                          >
                            Block #{block}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  /* SEARCH RESULTS VIEW */
                  <>
                    <div className="results-status-bar">
                      <span>
                        Showing <strong>{filteredData.length}</strong> of <strong>{totalMatchingRecords.length.toLocaleString()}</strong> Matching Voters
                      </span>
                      {searchQuery && <span className="query-hint">Query: "{searchQuery}"</span>}
                    </div>

                    <div className="voter-list">
                      {filteredData.length === 0 ? (
                        <div className="empty-state">
                          <UserCheck size={48} className="text-gray-400" />
                          <h3>No Matching Voters Found</h3>
                          <p>Check the CNIC number or spelling and try again.</p>
                        </div>
                      ) : (
                        <>
                          {filteredData.map((voter, idx) => renderVoterCard(voter, idx, false))}
                          
                          {/* Load More Button if more matching records exist */}
                          {displayLimit < totalMatchingRecords.length && (
                            <button 
                              className="load-more-btn"
                              onClick={() => setDisplayLimit(prev => prev + 50)}
                            >
                              <Plus size={18} />
                              Load More Matching Voters ({totalMatchingRecords.length - displayLimit} remaining)
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}

            {/* TAB 2: HOUSEHOLDS (FAMILIES) */}
            {activeTab === 'families' && (
              <div className="families-tab-view fade-in">
                <div className="search-box-wrapper">
                  <div className="search-field-container">
                    <Search size={18} className="search-icon" />
                    <input 
                      type="text" 
                      placeholder="Search by Gharana No, Block, or Member Name..." 
                      value={familySearchQuery}
                      onChange={(e) => setFamilySearchQuery(e.target.value)}
                    />
                    {familySearchQuery && (
                      <button className="clear-search-btn" onClick={() => setFamilySearchQuery('')}>
                        <X size={16} />
                      </button>
                    )}
                  </div>
                </div>

                <div className="results-status-bar">
                  <span>Showing {filteredFamilies.length} Households</span>
                </div>

                <div className="family-grid">
                  {filteredFamilies.map((fam) => (
                    <div key={fam.id} className="family-summary-card" onClick={() => setSelectedFamilyId(fam.id)}>
                      <div className="fam-card-head">
                        <div className="fam-head-title">
                          <Users size={20} className="text-emerald-500" />
                          <span>Gharana #{fam.gharanaNo}</span>
                        </div>
                        <span className="fam-member-badge">{fam.members.length} Members</span>
                      </div>
                      
                      <div className="fam-head-details">
                        <span className="detail-chip"><MapPin size={12} /> Block {fam.blockCode}</span>
                        {fam.members[0] && (
                          <span className="detail-head-name">
                            Head: {fam.members[0].NameUrdu || fam.members[0].CNIC}
                          </span>
                        )}
                      </div>

                      <button className="fam-view-link">
                        View Complete Gharana Members List <ChevronRight size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: STATS ANALYTICS */}
            {activeTab === 'stats' && statistics && (
              <div className="stats-tab-view fade-in">
                <div className="stats-hero-card">
                  <div className="stats-hero-top">
                    <BarChart3 size={28} className="text-emerald-500" />
                    <h3>Mardwal Constituency Metrics</h3>
                  </div>
                  <div className="stats-numbers-grid">
                    <div className="stat-box">
                      <span className="stat-val">{statistics.total.toLocaleString()}</span>
                      <span className="stat-lbl">Total Voters</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-val">{statistics.totalFamilies.toLocaleString()}</span>
                      <span className="stat-lbl">Total Households</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-val">{statistics.avgFamilySize}</span>
                      <span className="stat-lbl">Avg / Gharana</span>
                    </div>
                  </div>
                </div>

                {/* Gender Ratio Bar */}
                <div className="stats-card">
                  <h4>Gender Distribution Ratio</h4>
                  <div className="gender-bar-container">
                    <div className="gender-bar male-bar" style={{ width: `${statistics.malePercent}%` }}>
                      <span>{statistics.malePercent}% Male</span>
                    </div>
                    <div className="gender-bar female-bar" style={{ width: `${statistics.femalePercent}%` }}>
                      <span>{statistics.femalePercent}% Female</span>
                    </div>
                  </div>
                  <div className="gender-legend">
                    <div><span className="legend-dot male"></span> Male: {statistics.males.toLocaleString()}</div>
                    <div><span className="legend-dot female"></span> Female: {statistics.females.toLocaleString()}</div>
                  </div>
                </div>

                {/* Age Categories */}
                <div className="stats-card">
                  <h4>Age Group Breakdown</h4>
                  <div className="age-group-list">
                    <div className="age-item">
                      <span className="age-lbl">Youth (18 - 30 yrs)</span>
                      <span className="age-val">{statistics.youth.toLocaleString()} voters</span>
                    </div>
                    <div className="age-item">
                      <span className="age-lbl">Middle Age (31 - 50 yrs)</span>
                      <span className="age-val">{statistics.middle.toLocaleString()} voters</span>
                    </div>
                    <div className="age-item">
                      <span className="age-lbl">Seniors (50+ yrs)</span>
                      <span className="age-val">{statistics.seniors.toLocaleString()} voters</span>
                    </div>
                  </div>
                </div>

                {/* Full PDF Download Card */}
                <div className="stats-card">
                  <h4>Official Document Download</h4>
                  <button className="download-full-pdf-hero-btn" onClick={downloadFullPdfDocument}>
                    <Download size={18} />
                    Download Official 2023 Electoral PDF (299 Pages)
                  </button>
                </div>
              </div>
            )}

            {/* TAB 4: BOOKMARKS */}
            {activeTab === 'bookmarks' && (
              <div className="bookmarks-tab-view fade-in">
                <div className="results-status-bar">
                  <span>Saved Pinned Voters ({bookmarkedVoters.length})</span>
                </div>

                {bookmarkedVoters.length === 0 ? (
                  <div className="empty-state">
                    <Bookmark size={48} className="text-gray-400" />
                    <h3>No Bookmarked Voters</h3>
                    <p>Tap the bookmark icon on any voter card to pin them here for quick field access.</p>
                  </div>
                ) : (
                  <div className="voter-list">
                    {bookmarkedVoters.map((voter, idx) => renderVoterCard(voter, idx, false))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Interactive Zoom Modal Viewer */}
      <AnimatePresence>
        {zoomModalImage && (
          <motion.div 
            className="modal-backdrop z-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setZoomModalImage(null)}
          >
            <div className="zoom-modal-content" onClick={e => e.stopPropagation()}>
              <div className="zoom-modal-toolbar">
                <span>High-Resolution Document Viewer</span>
                <div className="zoom-btn-controls">
                  <button onClick={() => setModalZoomScale(prev => Math.min(prev + 0.5, 4))}>
                    <ZoomIn size={18} />
                  </button>
                  <button onClick={() => setModalZoomScale(prev => Math.max(prev - 0.5, 0.8))}>
                    <ZoomOut size={18} />
                  </button>
                  <button onClick={() => setModalZoomScale(1)}>Reset</button>
                  <button 
                    className="save-modal-btn"
                    onClick={() => downloadImageToGallery(zoomModalImage, 'Voter_Document_Frame.jpg')}
                  >
                    <Download size={16} />
                    Save
                  </button>
                  <button onClick={() => setZoomModalImage(null)}><X size={20} /></button>
                </div>
              </div>

              <div className="zoom-image-wrapper">
                <img 
                  src={zoomModalImage} 
                  alt="Zoomed View"
                  style={{ transform: `scale(${modalZoomScale})` }}
                  className="zoomed-img"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filter Drawer Modal */}
      <AnimatePresence>
        {showFilterDrawer && (
          <motion.div 
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowFilterDrawer(false)}
          >
            <motion.div 
              className="filter-drawer"
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 220 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="drawer-header">
                <h3>Filter Voter List</h3>
                <button onClick={() => setShowFilterDrawer(false)}><X size={20} /></button>
              </div>

              <div className="drawer-body">
                {/* Gender Options */}
                <div className="filter-group">
                  <label>Gender</label>
                  <div className="filter-options-grid">
                    {['all', 'Male', 'Female'].map(g => (
                      <button 
                        key={g} 
                        className={`filter-opt-btn ${genderFilter === g ? 'active' : ''}`}
                        onClick={() => setGenderFilter(g)}
                      >
                        {g === 'all' ? 'All' : g}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Age Options */}
                <div className="filter-group">
                  <label>Age Range</label>
                  <div className="filter-options-grid">
                    {['all', '18-30', '31-50', '50+'].map(a => (
                      <button 
                        key={a} 
                        className={`filter-opt-btn ${ageFilter === a ? 'active' : ''}`}
                        onClick={() => setAgeFilter(a)}
                      >
                        {a === 'all' ? 'All Ages' : `${a} Yrs`}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Block Code Options */}
                <div className="filter-group">
                  <label>Block Code</label>
                  <select 
                    value={blockFilter} 
                    onChange={(e) => setBlockFilter(e.target.value)}
                    className="filter-select"
                  >
                    <option value="all">All Block Codes</option>
                    {availableBlockCodes.map(block => (
                      <option key={block} value={block}>Block {block}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="drawer-footer">
                <button 
                  className="reset-btn"
                  onClick={() => {
                    setGenderFilter('all');
                    setBlockFilter('all');
                    setAgeFilter('all');
                  }}
                >
                  Reset
                </button>
                <button className="apply-btn" onClick={() => setShowFilterDrawer(false)}>
                  Apply Filters
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Printable Digital Voter Slip Modal */}
      <AnimatePresence>
        {printVoter && (
          <motion.div 
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setPrintVoter(null)}
          >
            <motion.div 
              className="voter-slip-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="slip-modal-header">
                <h3>Official Voter Slip</h3>
                <button onClick={() => setPrintVoter(null)}><X size={20} /></button>
              </div>

              <div className="voter-printable-slip" id="voter-slip">
                <div className="slip-brand">
                  <ShieldCheck size={28} className="text-emerald-600" />
                  <div>
                    <h2>Election Commission of Pakistan</h2>
                    <p>Constituency NA-88 / PP-84 Khushab (Mardwal)</p>
                  </div>
                </div>

                <div className="slip-body">
                  <div className="slip-row">
                    <span className="slip-lbl">CNIC Number:</span>
                    <span className="slip-val cnic">{printVoter.CNIC}</span>
                  </div>
                  <div className="slip-row">
                    <span className="slip-lbl">Voter Name (نام):</span>
                    <span className="slip-val urdu">{printVoter.NameUrdu}</span>
                  </div>
                  <div className="slip-row">
                    <span className="slip-lbl">Father/Husband (ولدیت):</span>
                    <span className="slip-val urdu">{printVoter.FatherNameUrdu}</span>
                  </div>
                  <div className="slip-row">
                    <span className="slip-lbl">Polling Station:</span>
                    <span className="slip-val font-bold">{getPollingStation(printVoter.BlockCode, printVoter.Gender)}</span>
                  </div>
                  <div className="slip-grid-3">
                    <div>
                      <span className="slip-lbl">Silsila No</span>
                      <span className="slip-val">#{printVoter.SilsilaNo}</span>
                    </div>
                    <div>
                      <span className="slip-lbl">Gharana No</span>
                      <span className="slip-val">#{printVoter.GharanaNo}</span>
                    </div>
                    <div>
                      <span className="slip-lbl">Block Code</span>
                      <span className="slip-val">{printVoter.BlockCode}</span>
                    </div>
                  </div>
                </div>

                <div className="slip-footer">
                  <p>Verified digital slip generated from official constituency database.</p>
                </div>
              </div>

              <div className="slip-actions">
                <button className="print-now-btn" onClick={() => window.print()}>
                  <Printer size={18} /> Print Voter Slip
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Fixed Bottom Navigation Bar */}
      <nav className="bottom-nav-bar">
        <button 
          className={`nav-item ${activeTab === 'home' && !selectedFamilyId ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('home');
            setSelectedFamilyId(null);
          }}
        >
          <Home size={20} />
          <span>Home</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'families' || selectedFamilyId ? 'active' : ''}`}
          onClick={() => setActiveTab('families')}
        >
          <Users size={20} />
          <span>Households</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('stats');
            setSelectedFamilyId(null);
          }}
        >
          <BarChart3 size={20} />
          <span>Analytics</span>
        </button>

        <button 
          className={`nav-item ${activeTab === 'bookmarks' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('bookmarks');
            setSelectedFamilyId(null);
          }}
        >
          <Bookmark size={20} />
          <span>Bookmarks</span>
        </button>
      </nav>
    </div>
  );
}

export default App;
