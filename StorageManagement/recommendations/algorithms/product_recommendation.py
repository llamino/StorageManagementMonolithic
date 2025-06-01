# recommendations/algorithms/algorithms/product_recommendation.py
# توصیه‌گر ترکیبی برای محصولات (content-based + collaborative)
import time  # برای اندازه‌گیری زمان اجرا

import pandas as pd  # برای پردازش داده‌ها
from sklearn.preprocessing import StandardScaler  # برای نرمال‌سازی ویژگی‌ها
from sklearn.metrics.pairwise import cosine_similarity  # برای محاسبه شباهت کسینوسی
from sklearn.neighbors import NearestNeighbors  # برای KNN در collaborative filtering
import logging  # برای لاگ‌گیری
from typing import Dict, List, Any, Tuple  # تایپینگ برای توابع
import logging.config  # برای پیکربندی لاگر

# مدل‌های Django مربوط به محصولات، سفارش‌ها و کاربران
from products.models import Product
from orders.models import Order
from users.models import User, Profile

# پیکربندی لاگر برای نمایش لاگ‌ها در کنسول
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# راه‌اندازی پیکربندی لاگر قبل از استفاده
logging.config.dictConfig(LOGGING)

# ایجاد لاگر با نام ماژول جاری
logger = logging.getLogger(__name__)


# کلاس اصلی توصیه‌گر ترکیبی
class HybridRecommender:
    def __init__(self):
        # مقیاس‌گذار استاندارد و KNN با معیار کسینوسی
        self.scaler = StandardScaler()
        self.knn = NearestNeighbors(n_neighbors=5, metric='cosine')

    def load_data(self) -> pd.DataFrame:
        try:
            # بارگذاری داده‌ها از CSV
            logger.info("Loading order items data from CSV...")
            df = pd.read_csv('recommendations/data/order_items_data.csv')
            logger.info(f"Raw data loaded: {df.shape[0]} rows")

            # فیلتر سفارش‌های پرداخت‌شده یا تحویل داده‌شده
            df = df[df['order_status'].isin(['paid', 'delivered'])]
            logger.info(f"Filtered paid/delivered orders: {df.shape[0]} rows")

            # پر کردن نمرات خالی کاربران با میانگین نمرات آن کاربر یا نمره میانگین محصول
            df['user_rating'] = df['user_rating'].fillna(df.groupby('user_id')['user_rating'].transform('mean'))
            df['user_rating'] = df['user_rating'].fillna(df['product_avg_score'])

            # پردازش دسته‌بندی‌ها به صورت لیست رشته‌ها
            df['product_categories'] = df['product_categories'].fillna('')
            df['product_categories'] = df['product_categories'].apply(
                lambda x: [cat.strip() for cat in str(x).split(',') if cat.strip()]
            )

            # نمایش چند نمونه برای بررسی صحت داده‌ها
            logger.debug("Sample processed data:\n" + df.head().to_string())
            return df
        except Exception as e:
            # در صورت بروز خطا
            logger.error(f"Error loading data: {str(e)}")
            raise

    def prepare_content_features(self, df: pd.DataFrame) -> pd.DataFrame:
        start = time.time()
        logger.info("Preparing content features...")

        # محاسبه حاشیه سود محصول
        df['profit_margin'] = (df['sell_price'] - df['buy_price']) / df['buy_price']
        numerical_features = ['profit_margin', 'product_avg_score', 'user_rating']

        # نرمال‌سازی ویژگی‌های عددی
        df[numerical_features] = self.scaler.fit_transform(df[numerical_features])

        # نمایش ویژگی‌های نرمال‌شده
        logger.debug(f"Scaled features:\n{df[numerical_features].head().to_string()}")

        # استخراج همه دسته‌بندی‌های یکتا
        all_categories = set()
        for categories in df['product_categories']:
            all_categories.update(categories)
        logger.info(f"Found {len(all_categories)} unique product categories")

        # ایجاد ویژگی دودویی برای هر دسته‌بندی
        for category in all_categories:
            df[f'category_{category}'] = df['product_categories'].apply(lambda x: 1 if category in x else 0)

        logger.info(f"Content features prepared in {time.time() - start:.2f} seconds")
        return df

    def prepare_collaborative_features(self, df: pd.DataFrame) -> pd.DataFrame:
        start = time.time()
        logger.info("Preparing collaborative filtering matrix...")

        # ساخت ماتریس کاربر-محصول با نمرات
        user_item_matrix = df.pivot_table(
            index='user_id',
            columns='product_name',
            values='user_rating',
            fill_value=0
        )

        # آموزش مدل KNN بر روی این ماتریس
        self.knn.fit(user_item_matrix)

        logger.info(f"User-item matrix shape: {user_item_matrix.shape} (prepared in {time.time() - start:.2f} seconds)")
        return user_item_matrix

    def get_content_recommendations(self, user_id: int, df: pd.DataFrame, n: int = 5) -> List[Tuple[str, float]]:
        try:
            logger.info(f"Generating content-based recommendations for user {user_id}...")
            user_ratings = df[df['user_id'] == user_id]

            if user_ratings.empty:
                logger.warning(f"No ratings found for user {user_id}")
                return []

            # بردار نماینده‌ی پروفایل کاربر از ویژگی‌های عددی
            user_profile_vector = user_ratings[
                ['profit_margin', 'user_rating', 'product_avg_score']].mean().values.reshape(1, -1)

            # استخراج بردارهای محصولات یکتا
            product_vectors = df.drop_duplicates('product_name')[
                ['product_name', 'profit_margin', 'user_rating', 'product_avg_score']]
            product_vectors = product_vectors.dropna()

            # محاسبه شباهت کسینوسی با هر محصول
            similarities = []
            for _, row in product_vectors.iterrows():
                vec = row[['profit_margin', 'user_rating', 'product_avg_score']].values.reshape(1, -1)
                sim = cosine_similarity(user_profile_vector, vec)[0][0]
                similarities.append((row['product_name'], sim))

            # مرتب‌سازی و انتخاب بهترین‌ها
            sorted_sims = sorted(similarities, key=lambda x: x[1], reverse=True)[:n]
            for product, score in sorted_sims:
                logger.debug(f"Content-based score - {product}: {score:.4f}")

            return sorted_sims
        except Exception as e:
            logger.error(f"Error in content recommendation: {e}")
            return []

    def get_collaborative_recommendations(self, user_id: int, matrix: pd.DataFrame, n: int = 5) -> List[str]:
        try:
            logger.info(f"Generating collaborative recommendations for user {user_id}...")
            if user_id not in matrix.index:
                logger.warning(f"User {user_id} not found in collaborative matrix")
                return []

            # بردار کاربر و پیدا کردن نزدیک‌ترین کاربران
            user_vector = pd.DataFrame([matrix.loc[user_id].values], columns=matrix.columns)
            distances, indices = self.knn.kneighbors(user_vector)

            similar_users = matrix.iloc[indices[0]]

            # میانگین نمرات کاربران مشابه
            recommendations = similar_users.mean().sort_values(ascending=False)

            # حذف آیتم‌هایی که قبلاً توسط کاربر مشاهده یا امتیاز داده شده‌اند
            already_rated = matrix.loc[user_id]
            recommendations = recommendations[already_rated == 0]

            # انتخاب n محصول برتر
            top_recs = recommendations.head(n).index.tolist()
            for product, score in recommendations.head(n).items():
                logger.debug(f"Collaborative score - {product}: {score:.4f}")

            return top_recs
        except Exception as e:
            logger.error(f"Error in collaborative recommendation: {e}")
            return []

    def get_hybrid_recommendations(self, user_email: str, n: int = 5) -> Dict[str, Any]:
        try:
            logger.info(f"Getting hybrid recommendations for user: {user_email}")

            # واکشی کاربر از دیتابیس بر اساس ایمیل
            user = User.objects.get(email=user_email)
            user_id = user.id
            logger.info(f"User ID resolved: {user_id}")

            # اجرای مراحل توصیه‌گر
            df = self.load_data()
            df = self.prepare_content_features(df)
            matrix = self.prepare_collaborative_features(df)

            content_recs = self.get_content_recommendations(user_id, df, n)
            collab_recs = self.get_collaborative_recommendations(user_id, matrix, n)

            # تنظیم وزن‌دهی بر اساس تعداد سفارش
            order_count = Order.objects.filter(user=user).count()
            if order_count == 0:
                alpha, beta, reason = 0.7, 0.3, "new user (cold start)"
            elif order_count < 5:
                alpha, beta, reason = 0.5, 0.5, "few orders"
            else:
                alpha, beta, reason = 0.3, 0.7, "experienced user"

            logger.info(f"Order count: {order_count} | alpha: {alpha}, beta: {beta} ({reason})")

            final = {}

            # افزودن توصیه‌های content-based به دیکشنری نهایی با وزن alpha
            for name, score in content_recs:
                final[name] = {'score': score * alpha, 'source': 'content'}

            # افزودن توصیه‌های collaborative به دیکشنری با وزن beta
            for name in collab_recs:
                if name not in final:
                    final[name] = {'score': beta, 'source': 'collaborative'}

            # مرتب‌سازی توصیه‌ها بر اساس امتیاز نهایی
            sorted_products = sorted(final.items(), key=lambda x: x[1]['score'], reverse=True)

            results = []
            for product_name, data in sorted_products:
                # بررسی وجود محصول در دیتابیس
                product = Product.objects.filter(name=product_name).first()
                if not product:
                    logger.warning(f"Product '{product_name}' not found in DB, skipping...")
                    continue
                if not product.productproperty_set.filter(total_stock__gte=3).exists():
                    logger.warning(f"Product '{product_name}' has insufficient stock, skipping...")
                    continue

                # آماده‌سازی نتیجه نهایی توصیه‌شده
                result = {
                    'product_name': product.name,
                    'product_image': product.image.url if product.image else None,
                    'product_avg_score': product.avg_score,
                    'score': round(data['score'], 3),
                    'source': data['source']
                }
                results.append(result)
                logger.debug(f"Added final recommendation: {result}")

                # محدود کردن به n نتیجه
                if len(results) >= n:
                    break

            logger.info(f"Final recommendation count: {len(results)}")
            return {
                'success': True,
                'recommendations': results,
                'metadata': {
                    'user_order_count': order_count,
                    'alpha': alpha,
                    'beta': beta,
                    'reason': reason
                }
            }
        except Exception as e:
            logger.error(f"Hybrid recommendation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
