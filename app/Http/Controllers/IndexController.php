<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;

class IndexController extends Controller {
    private $bid = 50;

    function __invoke() {
        $old_prices = DB::table('stats')->get();
        $new_prices = $this->getNewPrices();
        $comparison = collect();

        foreach ($new_prices as $item) {
            $old_stats = $old_prices->where('symbol', $item['symbol'])->first();

            if ($item['price'] && $old_stats) {
                $delta_price = number_format(100 * ($item['price'] - $old_stats->price) / $old_stats->price, 2);
                $delta_volume = number_format(100 * ($item['volume'] - $old_stats->volume) / $old_stats->volume, 2);

                $comparison->add([
                    'symbol' => $item['symbol'],
                    'delta_price' => $delta_price,
                    'delta_volume' => $delta_volume,
                    'price' => $item['price']
                ]);
            }
        }

        // var_dump($comparison);

        if ($comparison->count()) {
            // $item = $comparison->where('delta_price', '>', 0)->sortByDesc('confidence')->first();
            $item = $comparison->shuffle()->first();

            // var_dump($item);
            // var_dump($this->getActiveTrades()->whereIn('symbol', $item['symbol'])->count());
            // var_dump(!DB::table('trades')->where('symbol', $item['symbol'])->where('buy_time', '>=' , date('Y-m-d H:i:s', strtotime('-6 hour')))->count());

            // if (!$this->getActiveTrades()->whereIn('symbol', $item['symbol'])->count() && $this->getFunds() > $this->bid &&
                // !DB::table('trades')->where('symbol', $item['symbol'])->where('buy_time', '>=' , date('Y-m-d H:i:s', strtotime('-6 hour')))->count()) 
            $this->buy($item);
        }
    }

    function getNewPrices() {
        $response = Http::get('https://api.binance.com/api/v3/ticker/24hr');

        foreach (json_decode($response->body()) as $item) {
            if (strpos($item->symbol, 'USDT') !== false && strpos($item->symbol, 'DOWN') === false && strpos($item->symbol, 'UP') === false && $item->lastPrice > 0) {
                $new_prices[] = [
                    'symbol' => $item->symbol,
                    'price' => $item->lastPrice,
                    'volume' => $item->quoteVolume
                ];
            }
        }
        
        DB::transaction(function() use ($new_prices) {
            DB::table('stats')->truncate();
            DB::table('stats')->insert($new_prices);
            $this->updateActiveTrades($new_prices);
        });

        return $new_prices;
    }

    function getFunds() {
        return DB::table('wallet')->first()->funds;
    }

    function getActiveTrades() {
        return DB::table('trades')->where('status', 'active')->get();
    }

    function updateActiveTrades($new_prices) {
        foreach ($this->getActiveTrades() as $item) {
            foreach ($new_prices as $new_price) {
                if ($item->symbol == $new_price['symbol']) {
                    if ($item->top_price < $new_price['price']) {
                        DB::table('trades')->where('symbol', $item->symbol)->where('status', 'active')->update(['top_price' => $new_price['price']]);
                    }
                    
                    // var_dump('ATH: ' . $item->top_price);
                    // var_dump('Price: ' . $new_price['price']);
                    // var_dump(number_format(100 * ($item->buy_price - $new_price['price']) / $new_price['price'], 2));
                    // var_dump(number_format(100 * ($item->top_price - $new_price['price']) / $new_price['price'], 2));

                    if (number_format(100 * ($new_price['price'] - $item->buy_price) / $item->buy_price, 2) > 2 ||
                        number_format(100 * ($item->buy_price - $new_price['price']) / $new_price['price'], 2) > 2) {
                        $this->sell($new_price, $item->buy_price);
                    }

                    break;
                }
            }
        }
    }

    function buy($item) {
        DB::transaction(function() use ($item) {
            DB::table('trades')->insert([
                'symbol' => $item['symbol'],
                'delta_price' => $item['delta_price'],
                'delta_volume' => $item['delta_volume'],
                'buy_price' => $item['price'],
                'top_price' => $item['price'],
                'buy_time' => date('Y-m-d H:i:s'),
                'status' => 'active'
            ]);

            DB::table('wallet')->update([
                'funds' => DB::raw("`funds` - $this->bid")
            ]);
        });

        echo 'Bought ' . $item['symbol'];
    }

    function sell($item, $old_price) {
        $profit = $this->bid * ($item['price'] / $old_price - 1);

        DB::table('trades')->where('symbol', $item['symbol'])->where('status', 'active')->update([
            'status' => 'finished',
            'sell_price' => $item['price'],
            'profit' => $profit,
            'sell_time' => date('Y-m-d H:i:s')
        ]);

        DB::table('wallet')->update([
            'funds' => DB::raw("`funds` + $this->bid + $profit"),
        ]);

        echo 'Sold ' . $item['symbol'];
    }

    function clean() {
        DB::table('stats')->truncate();
        DB::table('trades')->truncate();
        DB::table('wallet')->update([
            'funds' => 100,
            'profit' => 0
        ]);
    }
}
