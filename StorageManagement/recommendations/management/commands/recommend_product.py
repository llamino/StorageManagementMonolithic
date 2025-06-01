# recommendations/management/commands/recommend_product.py
from typing import Any
from django.core.management.base import BaseCommand
from django.utils import timezone

from recommendations.algorithms.product_recommendation import HybridRecommender
from users.models import User
from recommendations.models import UserRecommendation
from recommendations.serializers import HybridRecommendationSerializer



class Command(BaseCommand):
    help = 'Run hybrid recommendation algorithm for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_email',
            type=str,
            help='Run for a specific user email',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting recommendation algorithm...'))

            if options['user_email']:
                users = User.objects.filter(email=options['user_email'])
            else:
                users = User.objects.all()

            for user in users:
                recommender = HybridRecommender()
                result = recommender.get_hybrid_recommendations(user_email=user.email)

                if not result['success']:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping {user.email}, error: {result["error"]}'
                    ))
                    continue

                serializer = HybridRecommendationSerializer(result['recommendations'], many=True)
                json_data = {
                    'recommendations': serializer.data,
                    'metadata': result.get('metadata', {})
                }

                UserRecommendation.objects.update_or_create(
                    user=user,
                    defaults={'data': json_data}
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully updated recommendations for {user.email}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
