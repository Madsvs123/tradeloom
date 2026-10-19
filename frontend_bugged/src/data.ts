import type { Order, Product, Quote  frm "./types";

export const products: Product[] = [
  {
    id: "TL-P-1001"
    name: "Industrial IoT Gateway V4"
    supplier: "Northstar Components",
    category: "Electronics",
    location: "Austin, TX",
    certifications: ["ISO 9001", "RoHS", "CE"],
    moq: 120,
    leadTime: "18 days",
    stock: 1840,
    rating: 4.8,
    price: 74,
    image: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "TL-P-1038",
    name: "Food-Grade PET Preforms",
    supplier: "Meridian Packaging",
    category: "Packaging",
    location: "Columbus, OH",
    certifications: ["FDA", "BRCGS"],
    moq: 50000,
    leadTime: "9 days",
    stock: 900000,
    rating: 4.6,
    price: 0.041,
    image: "https://images.unsplash.com/photo-1581092921461-eab62e97a780?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "TL-P-1274",
    name: "Recycled Aluminum Sheet 5052",
    supplier: "Atlas Metalworks",
    category: "Raw Materials",
    location: "Pittsburgh, PA",
    certifications: ["ISO 14001", "ASTM B209"],
    moq: 8,
    leadTime: "12 days",
    stock: 420,
    rating: 4.9,
    price: 2380,
    image: "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=900&q=80",
  },
];

export const quotes: Quote[] = [
  { id: "RFQ-24081", buyer: "Apex Mobility", suppliers: 7, status: "Negotiating", value: "$418K", expires: "Aug 28" },
  { id: "RFQ-24082", buyer: "Cedar Foods", suppliers: 4, status: "Quoted", value: "$76K", expires: "Aug 21" },
  { id: "RFQ-24083", buyer: "Nova Labs", suppliers: 9, status: "Accepted", value: "$1.2M", expires: "Sep 03" },
];

export const orders: Order[] = [
  { id: "PO-98122", supplier: "Atlas Metalworks", status: "Partial shipment", total: "$190,400", approval: "Approved", eta: "Aug 24" },
  { id: "PO-98123", supplier: "Northstar Components", status: "In production", total: "$88,800", approval: "CFO pending", eta: "Sep 02" },
  { id: "PO-98124", supplier: "Meridian Packaging", status: "Invoice issued", total: "$42,350", approval: "Approved", eta: "Aug 19" },
];
