>
import { Router } from 'express';
import Product from '../models/Product.js';

const router = Router();

/**
 * GET /api/products
 * Returns a list of products with optional pagination.
 */
router.get('/', async (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(100, parseInt(req.query.limit) || 20);
    const skip = (page - 1) * limit;

    const products = await Product.find()
      .skip(skip)
      .limit(limit)
      .select('-__v'); // hide internal field

    res.json({ data: products, pagination: { page, limit, skip } });
  } catch (err) {
    console.error('Error fetching products:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/products/:id
 * Returns a single product by its primary key.
 */
router.get('/:id', async (req, res) => {
  try {
    const product = await Product.findById(req.params.id).select('-__v');
    if (!product) return res.status(404).json({ error: 'Product not found' });

    res.json({ data: product });
  } catch (err) {
    console.error('Error fetching product:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;