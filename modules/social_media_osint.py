import requests
from datetime import datetime
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class SocialMediaOSINT:
    def __init__(self):
        self.platforms = {
            'github': {
                'url': 'https://api.github.com/users/',
                'check_method': 'api'
            },
            'twitter': {
                'url': 'https://twitter.com/',
                'check_method': 'web'
            },
            'instagram': {
                'url': 'https://www.instagram.com/',
                'check_method': 'web'
            },
            'linkedin': {
                'url': 'https://www.linkedin.com/in/',
                'check_method': 'web'
            },
            'facebook': {
                'url': 'https://www.facebook.com/',
                'check_method': 'web'
            },
            'reddit': {
                'url': 'https://www.reddit.com/user/',
                'check_method': 'api'
            },
            'youtube': {
                'url': 'https://www.youtube.com/@',
                'check_method': 'web'
            },
            'tiktok': {
                'url': 'https://www.tiktok.com/@',
                'check_method': 'web'
            },
            'pinterest': {
                'url': 'https://www.pinterest.com/',
                'check_method': 'web'
            },
            'medium': {
                'url': 'https://medium.com/@',
                'check_method': 'web'
            },
            'twitch': {
                'url': 'https://www.twitch.tv/',
                'check_method': 'web'
            },
            'snapchat': {
                'url': 'https://www.snapchat.com/add/',
                'check_method': 'web'
            },
            'telegram': {
                'url': 'https://t.me/',
                'check_method': 'web'
            },
            'discord': {
                'url': 'https://discord.com/users/',
                'check_method': 'custom'
            },
            'spotify': {
                'url': 'https://open.spotify.com/user/',
                'check_method': 'web'
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_username(self, username):
        """Search username across all platforms"""
        result = {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'platforms_found': [],
            'platforms_not_found': [],
            'platforms_error': [],
            'detailed_results': {},
            'statistics': {}
        }
        
        # Use threading for parallel checks
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_platform = {
                executor.submit(self.check_platform, platform, username, info): platform
                for platform, info in self.platforms.items()
            }
            
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    platform_result = future.result()
                    result['detailed_results'][platform] = platform_result
                    
                    if platform_result.get('exists') == True:
                        result['platforms_found'].append(platform)
                    elif platform_result.get('exists') == False:
                        result['platforms_not_found'].append(platform)
                    else:
                        result['platforms_error'].append(platform)
                except Exception as e:
                    result['detailed_results'][platform] = {'error': str(e)}
                    result['platforms_error'].append(platform)
        
        # Generate statistics
        result['statistics'] = {
            'total_platforms_checked': len(self.platforms),
            'found': len(result['platforms_found']),
            'not_found': len(result['platforms_not_found']),
            'errors': len(result['platforms_error']),
            'success_rate': f"{(len(result['platforms_found']) / len(self.platforms) * 100):.2f}%"
        }
        
        return result
    
    def check_platform(self, platform, username, info):
        """Check if username exists on a specific platform"""
        result = {
            'platform': platform,
            'exists': None,
            'url': f"{info['url']}{username}",
            'profile_data': {},
            'last_checked': datetime.now().isoformat()
        }
        
        try:
            if info['check_method'] == 'api':
                if platform == 'github':
                    result = self.check_github(username)
                elif platform == 'reddit':
                    result = self.check_reddit(username)
            elif info['check_method'] == 'web':
                result = self.check_web_presence(platform, username, info['url'])
            else:
                result['exists'] = None
                result['error'] = 'Check method not implemented'
        except Exception as e:
            result['error'] = str(e)
            result['exists'] = None
        
        return result
    
    def check_github(self, username):
        """Check GitHub profile with detailed info"""
        url = f"https://api.github.com/users/{username}"
        result = {
            'platform': 'github',
            'exists': False,
            'url': f"https://github.com/{username}",
            'profile_data': {}
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['exists'] = True
                result['profile_data'] = {
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'company': data.get('company'),
                    'location': data.get('location'),
                    'email': data.get('email'),
                    'blog': data.get('blog'),
                    'twitter_username': data.get('twitter_username'),
                    'public_repos': data.get('public_repos'),
                    'public_gists': data.get('public_gists'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'avatar_url': data.get('avatar_url')
                }
                
                # Get repositories
                repos_url = f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated"
                repos_response = requests.get(repos_url, headers=self.headers, timeout=10)
                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    result['profile_data']['recent_repos'] = [
                        {
                            'name': r.get('name'),
                            'description': r.get('description'),
                            'language': r.get('language'),
                            'stars': r.get('stargazers_count'),
                            'url': r.get('html_url')
                        }
                        for r in repos[:5]
                    ]
            elif response.status_code == 404:
                result['exists'] = False
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_reddit(self, username):
        """Check Reddit profile with detailed info"""
        url = f"https://www.reddit.com/user/{username}/about.json"
        result = {
            'platform': 'reddit',
            'exists': False,
            'url': f"https://www.reddit.com/user/{username}",
            'profile_data': {}
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {})
                result['exists'] = True
                result['profile_data'] = {
                    'name': user_data.get('name'),
                    'id': user_data.get('id'),
                    'created_utc': user_data.get('created_utc'),
                    'link_karma': user_data.get('link_karma'),
                    'comment_karma': user_data.get('comment_karma'),
                    'total_karma': user_data.get('total_karma'),
                    'is_gold': user_data.get('is_gold'),
                    'is_mod': user_data.get('is_mod'),
                    'verified': user_data.get('verified'),
                    'has_verified_email': user_data.get('has_verified_email'),
                    'icon_img': user_data.get('icon_img')
                }
                
                # Get recent posts
                posts_url = f"https://www.reddit.com/user/{username}/submitted.json?limit=5"
                posts_response = requests.get(posts_url, headers=self.headers, timeout=10)
                if posts_response.status_code == 200:
                    posts_data = posts_response.json()
                    posts = posts_data.get('data', {}).get('children', [])
                    result['profile_data']['recent_posts'] = [
                        {
                            'title': p.get('data', {}).get('title'),
                            'subreddit': p.get('data', {}).get('subreddit'),
                            'score': p.get('data', {}).get('score'),
                            'url': f"https://reddit.com{p.get('data', {}).get('permalink')}"
                        }
                        for p in posts[:5]
                    ]
            elif response.status_code == 404:
                result['exists'] = False
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_web_presence(self, platform, username, base_url):
        """Generic web presence check"""
        url = f"{base_url}{username}"
        result = {
            'platform': platform,
            'exists': None,
            'url': url,
            'profile_data': {}
        }
        
        try:
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                result['exists'] = True
                result['profile_data']['status'] = 'Profile likely exists'
                result['profile_data']['final_url'] = response.url
            elif response.status_code == 404:
                result['exists'] = False
                result['profile_data']['status'] = 'Profile not found'
            elif response.status_code in [301, 302, 303, 307, 308]:
                result['exists'] = True
                result['profile_data']['status'] = 'Profile exists (redirected)'
                result['profile_data']['final_url'] = response.url
            else:
                result['exists'] = None
                result['profile_data']['status'] = f'HTTP {response.status_code}'
        except requests.exceptions.Timeout:
            result['exists'] = None
            result['error'] = 'Request timeout'
        except requests.exceptions.RequestException as e:
            result['exists'] = None
            result['error'] = str(e)
        
        return result
    
    def analyze_profile(self, platform, username):
        """Deep analysis of a specific platform profile"""
        if platform.lower() == 'github':
            return self.analyze_github_deep(username)
        elif platform.lower() == 'reddit':
            return self.analyze_reddit_deep(username)
        else:
            return self.check_platform(platform, username, self.platforms.get(platform, {}))
    
    def analyze_github_deep(self, username):
        """Deep GitHub analysis with activity patterns"""
        result = self.check_github(username)
        
        if result.get('exists'):
            try:
                # Get contribution activity
                events_url = f"https://api.github.com/users/{username}/events/public?per_page=100"
                response = requests.get(events_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    events = response.json()
                    
                    # Analyze activity
                    activity_types = {}
                    repos_contributed = set()
                    languages_used = set()
                    
                    for event in events:
                        event_type = event.get('type')
                        activity_types[event_type] = activity_types.get(event_type, 0) + 1
                        
                        repo = event.get('repo', {}).get('name')
                        if repo:
                            repos_contributed.add(repo)
                    
                    result['profile_data']['activity_analysis'] = {
                        'total_recent_events': len(events),
                        'activity_types': activity_types,
                        'repos_contributed_to': list(repos_contributed),
                        'active_repos_count': len(repos_contributed)
                    }
            except Exception as e:
                result['deep_analysis_error'] = str(e)
        
        return result
    
    def analyze_reddit_deep(self, username):
        """Deep Reddit analysis with posting patterns"""
        result = self.check_reddit(username)
        
        if result.get('exists'):
            try:
                # Analyze subreddit activity
                posts_url = f"https://www.reddit.com/user/{username}/submitted.json?limit=100"
                response = requests.get(posts_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    subreddits = {}
                    total_score = 0
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        subreddit = post_data.get('subreddit')
                        score = post_data.get('score', 0)
                        
                        if subreddit:
                            subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
                        total_score += score
                    
                    result['profile_data']['activity_analysis'] = {
                        'total_posts_analyzed': len(posts),
                        'subreddits_posted_in': len(subreddits),
                        'top_subreddits': sorted(subreddits.items(), key=lambda x: x[1], reverse=True)[:10],
                        'average_score': total_score / len(posts) if posts else 0
                    }
            except Exception as e:
                result['deep_analysis_error'] = str(e)
        
        return result
    
    def search_by_email(self, email):
        """Find social media profiles associated with an email"""
        # This would use services like Gravatar, Skype, etc.
        result = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'profiles': []
        }
        
        # Check Gravatar
        try:
            import hashlib
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
            response = requests.head(gravatar_url, timeout=5)
            
            if response.status_code == 200:
                result['profiles'].append({
                    'platform': 'gravatar',
                    'exists': True,
                    'url': f"https://www.gravatar.com/{email_hash}"
                })
        except:
            pass
        
        return result