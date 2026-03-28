import React, { createContext, useState, useContext } from 'react';

const translations = {
  en: {
    dashboard: "Dashboard",
    upload: "Upload",
    verify: "Verification",
    recentUploads: "Recent Uploads",
    docId: "Document ID",
    fileInfo: "File Info",
    uploadDate: "Upload Date",
    status: "Status",
    action: "Action",
    uploadDoc: "Document Upload Queue",
    uploadDesc: "Upload single or batch documents here. Our OCR engine will queue, extract, and structure the data.",
    selectFiles: "Select Files",
    processDocs: "Process Documents",
    docImage: "Document Image",
    extractedData: "Extracted Data",
    confirmSubmit: "Confirm & Submit Form",
    potentialDuplicate: "Potential Duplicate Detected",
    duplicateDesc: "A record with a matching Name and Date of Birth already exists. Please review carefully before confirming.",
    docType: "Document Type",
    overrideType: "Change Type"
  },
  hi: {
    dashboard: "डैशबोर्ड",
    upload: "अपलोड करें",
    verify: "सत्यापन",
    recentUploads: "हालिया अपलोड",
    docId: "दस्तावेज़ आईडी",
    fileInfo: "फ़ाइल जानकारी",
    uploadDate: "अपलोड तिथि",
    status: "स्थिति",
    action: "कार्रवाई",
    uploadDoc: "दस्तावेज़ अपलोड कतार",
    uploadDesc: "यहां एकल या एकाधिक दस्तावेज़ अपलोड करें। हमारा ओसीआर इंजन डेटा निकालेगा और संरचना करेगा।",
    selectFiles: "फ़ाइलें चुनें",
    processDocs: "दस्तावेज़ प्रोसेस करें",
    docImage: "दस्तावेज़ छवि",
    extractedData: "निकाला गया डेटा",
    confirmSubmit: "पुष्टि करें और फ़ॉर्म जमा करें",
    potentialDuplicate: "संभावित डुप्लिकेट मिला",
    duplicateDesc: "समान नाम और जन्म तिथि वाला रिकॉर्ड पहले से मौजूद है। कृपया पुष्टि करने से पहले सावधानीपूर्वक समीक्षा करें।",
    docType: "दस्तावेज़ का प्रकार",
    overrideType: "प्रकार बदलें"
  },
  mr: {
    dashboard: "डॅशबोर्ड",
    upload: "अपलोड करा",
    verify: "पडताळणी",
    recentUploads: "अलीकडील वाहिनी",
    docId: "दस्तऐवज आयडी",
    fileInfo: "फाइल माहिती",
    uploadDate: "अपलोड तारीख",
    status: "स्थिती",
    action: "क्रिया",
    uploadDoc: "दस्तऐवज अपलोड रांग",
    uploadDesc: "येथे एकल किंवा एकाधिक दस्तऐवज अपलोड करा. आमचे ओसीआर इंजिन डेटा काढेल आणि संरचित करेल.",
    selectFiles: "फायली निवडा",
    processDocs: "दस्तऐवज प्रक्रिया करा",
    docImage: "दस्तऐवज प्रतिमा",
    extractedData: "काढलेला डेटा",
    confirmSubmit: "पुष्टी करा आणि फॉर्म सबमिट करा",
    potentialDuplicate: "संभाव्य डुप्लिकेट आढळले",
    duplicateDesc: "समान नाव आणि जन्मतारीख असलेली नोंद आधीच अस्तित्वात आहे. कृपया पुष्टी करण्यापूर्वी काळजीपूर्वक पुनरावलोकन करा.",
    docType: "दस्तऐवज प्रकार",
    overrideType: "प्रकार बदला"
  }
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState('en');

  const t = (key) => {
    return translations[lang][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
